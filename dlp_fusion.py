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
    """Main application class for DLP-Fusion toolkit"""

    def __init__(self, db_path="dlp_fusion.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        print(f"Connected to database: {self.db_path}")

    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def initialize_db(self):
        """Initialize database with schema"""
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
        """Load knowledge base from JSON file"""
        print(f"Loading knowledge base from: {kb_file}")

        with open(kb_file, "r", encoding="utf-8") as f:
            kb_data = json.load(f)

        cursor = self.conn.cursor()

        # -----------------------------
        # Load TBox
        # -----------------------------
        tbox = kb_data.get("tbox", {})

        # subClassOf
        for item in tbox.get("subClassOf", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Class (sub, super) VALUES (?, ?)",
                (item["sub"], item["super"]),
            )

        # subPropertyOf (new in Week 2)
        for item in tbox.get("subPropertyOf", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Property (sub, super) VALUES (?, ?)",
                (item["sub"], item["super"]),
            )

        # transitiveProperty
        for prop in tbox.get("transitiveProperty", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Transitive (property) VALUES (?)",
                (prop,),
            )

        # -----------------------------
        # Load ABox
        # -----------------------------
        abox = kb_data.get("abox", {})

        # types
        for item in abox.get("types", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Type (individual, class) VALUES (?, ?)",
                (item["individual"], item["class"]),
            )

        # relations (optional)
        for item in abox.get("relations", []):
            cursor.execute(
                "INSERT OR IGNORE INTO Rel (property, from_ind, to_ind) VALUES (?, ?, ?)",
                (item["property"], item["from"], item["to"]),
            )

        self.conn.commit()
        print("Knowledge base loaded successfully")

    def query(self, query_type, *args):
        """Execute a query against the knowledge base"""
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


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="DLP-Fusion: DL to Datalog translator and query engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    subparsers.add_parser("init", help="Initialize database")

    # load
    load_parser = subparsers.add_parser("load", help="Load knowledge base from JSON")
    load_parser.add_argument("file", help="JSON knowledge base file")

    # query
    query_parser = subparsers.add_parser("query", help="Execute a query")
    query_parser.add_argument(
        "type",
        choices=["type", "sub", "subprop"],
        help="Query type: type (instance), sub (class subsumption), subprop (property subsumption)",
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
