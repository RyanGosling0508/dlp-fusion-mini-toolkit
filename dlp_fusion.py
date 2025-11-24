"""
DLP-Fusion: DL to Datalog translator and query engine
Main CLI interface
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path


class DLPFusion:
    def __init__(self, db_path="dlp_fusion.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        print(f"Connected to database: {self.db_path}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def initialize_db(self):
        if not self.conn:
            self.connect()
        schema_file = Path(__file__).parent / "sql" / "schema.sql"
        if not schema_file.exists():
            print(f"Error: Schema file not found at {schema_file}")
            return
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        self.conn.executescript(schema_sql)
        self.conn.commit()
        print("Database schema initialized")

    def load_knowledge_base(self, kb_file):
        print(f"Loading knowledge base from: {kb_file}")
        with open(kb_file, "r", encoding="utf-8") as f:
            kb_data = json.load(f)

        cursor = self.conn.cursor()

        tbox = kb_data.get("tbox", {})

        for item in tbox.get("subClassOf", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Class (sub, super) VALUES (?, ?)",
                (item["sub"], item["super"]),
            )

        for item in tbox.get("subPropertyOf", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Property (sub, super) VALUES (?, ?)",
                (item["sub"], item["super"]),
            )

        for prop in tbox.get("transitiveProperty", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Transitive (property) VALUES (?)",
                (prop,),
            )

        for item in tbox.get("inverseOf", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Inverse (p, inv) VALUES (?, ?)",
                (item["p"], item["inv"]),
            )

        for item in tbox.get("domain", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Domain (property, class) VALUES (?, ?)",
                (item["property"], item["class"]),
            )

        for item in tbox.get("range", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Range (property, class) VALUES (?, ?)",
                (item["property"], item["class"]),
            )

        abox = kb_data.get("abox", {})

        for item in abox.get("types", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Type (individual, class) VALUES (?, ?)",
                (item["individual"], item["class"]),
            )

        for item in abox.get("relations", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Rel (property, from_ind, to_ind) VALUES (?, ?, ?)",
                (item["property"], item["from"], item["to"]),
            )

        self.conn.commit()

        self.materialize_inferences()

        print("Knowledge base loaded successfully")

    def materialize_inferences(self):
        cursor = self.conn.cursor()

        # 1) inverseOf: Rel(p,x,y) -> Rel(inv,y,x)
        cursor.execute("SELECT p, inv FROM Inverse")
        for row in cursor.fetchall():
            p, inv = row["p"], row["inv"]
            cursor.execute(
                """
                INSERT OR IGNORE INTO Rel(property, from_ind, to_ind)
                SELECT ?, r.to_ind, r.from_ind
                FROM Rel r
                WHERE r.property = ?
                """,
                (inv, p),
            )

        # 2) transitive roles: for each transitive property r, compute closure and insert into Rel
        cursor.execute("SELECT property FROM Transitive")
        trans_props = [r["property"] for r in cursor.fetchall()]

        for r in trans_props:
            cursor.execute(
                """
                WITH RECURSIVE tc(x, y) AS (
                    SELECT from_ind, to_ind FROM Rel WHERE property = ?
                    UNION
                    SELECT tc.x, r2.to_ind
                    FROM tc JOIN Rel r2
                      ON r2.from_ind = tc.y AND r2.property = ?
                )
                SELECT x, y FROM tc
                """,
                (r, r),
            )
            pairs = cursor.fetchall()
            for pxy in pairs:
                cursor.execute(
                    "INSERT OR IGNORE INTO Rel(property, from_ind, to_ind) VALUES (?, ?, ?)",
                    (r, pxy["x"], pxy["y"]),
                )

        # 3) domain typing: Rel(p,x,y) & Domain(p,C) -> Type(x,C)
        cursor.execute(
            """
            INSERT OR IGNORE INTO Type(individual, class)
            SELECT DISTINCT r.from_ind, d.class
            FROM Rel r JOIN Domain d
              ON r.property = d.property
            """
        )

        # 4) range typing: Rel(p,x,y) & Range(p,C) -> Type(y,C)
        cursor.execute(
            """
            INSERT OR IGNORE INTO Type(individual, class)
            SELECT DISTINCT r.to_ind, g.class
            FROM Rel r JOIN Range g
              ON r.property = g.property
            """
        )

        self.conn.commit()

    def query(self, query_type, *args):
        cursor = self.conn.cursor()

        if query_type == "type":
            if len(args) != 2:
                print("Error: type query requires 2 arguments")
                return
            individual, class_name = args
            print(f"Checking: Is '{individual}' an instance of '{class_name}'?")

            cursor.execute(
                "SELECT COUNT(*) FROM Type WHERE individual = ? AND class = ?",
                (individual, class_name),
            )
            result = cursor.fetchone()[0] > 0
            print(f"Result: {result}")

        elif query_type == "sub":
            if len(args) != 2:
                print("Error: sub query requires 2 arguments")
                return
            sub_class, super_class = args
            print(f"Checking: Is '{sub_class}' a subclass of '{super_class}'?")

            cursor.execute(
                "SELECT COUNT(*) FROM ClassClosure WHERE sub = ? AND super = ?",
                (sub_class, super_class),
            )
            result = cursor.fetchone()[0] > 0
            print(f"Result: {result}")

        elif query_type == "subprop":
            if len(args) != 2:
                print("Error: subprop query requires 2 arguments")
                return
            sub_r, super_r = args
            print(f"Checking: Is '{sub_r}' a subproperty of '{super_r}'?")

            cursor.execute(
                "SELECT COUNT(*) FROM PropertyClosure WHERE sub = ? AND super = ?",
                (sub_r, super_r),
            )
            result = cursor.fetchone()[0] > 0
            print(f"Result: {result}")

        else:
            print(f"Unknown query type: {query_type}")

    def debug_rel(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT property, from_ind, to_ind FROM Rel ORDER BY property, from_ind, to_ind")
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))


def main():
    parser = argparse.ArgumentParser(
        description="DLP-Fusion: DL to Datalog translator and query engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("init", help="Initialize database")

    load_parser = subparsers.add_parser("load", help="Load knowledge base from JSON")
    load_parser.add_argument("file", help="JSON knowledge base file")

    query_parser = subparsers.add_parser("query", help="Execute a query")
    query_parser.add_argument(
        "type",
        choices=["type", "sub", "subprop"],
        help="Query type: type, sub, subprop",
    )
    query_parser.add_argument("args", nargs="+", help="Query arguments")

    args = parser.parse_args()
    dlp = DLPFusion()

    try:
        if args.command == "init":
            dlp.initialize_db()

        elif args.command == "load":
            dlp.connect()
            dlp.initialize_db()
            dlp.load_knowledge_base(args.file)

        elif args.command == "query":
            dlp.connect()
            dlp.query(args.type, *args.args)

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    finally:
        dlp.disconnect()


if __name__ == "__main__":
    main()
