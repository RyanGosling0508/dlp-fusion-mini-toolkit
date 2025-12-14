# DLP-Fusion Mini-Toolkit

### CSE498-46 Knowledge Representation — Final Project Deliverable

### Author: Yutong Chen

DLP-Fusion is an **Implementation-type final project** for CSE498-46 Knowledge Representation.
It delivers a fully functional reasoning toolkit that translates a **DHL fragment of Description Logic** into a Datalog-style rule system executed on **SQLite**, supporting inference and DL-style queries.

---

## 1. Project Purpose

DLP-Fusion demonstrates how DL knowledge can be operationalized through lightweight logic-programming techniques.
It loads a structured JSON knowledge base, translates TBox/ABox assertions into relational tables, materializes inferences via SQL rules, and exposes a simple CLI for answering DL-style queries.


---

## 2. Supported DHL Fragment

The system supports a Horn-style DHL subset frequently used in DLP research.

### **TBox Constructs**

* `subClassOf(C, D)` — subclass axioms
* `subPropertyOf(R, S)` — subproperty axioms
* `inverseOf(R, S)` — inverse roles
* `domain(R, C)` — domain typing
* `range(R, C)` — range typing
* `transitiveProperty(R)` — transitive roles

### **ABox Assertions**

* `Type(a, C)` — individual typing
* `Rel(R, a, b)` — binary role assertions

This fragment is sufficient for demonstrating the DLP intersection of DL and logic programming.

---

## 3. Project Structure

```
project/
│
├── dlp_fusion.py           # main reasoning engine + CLI interface
├── requirements.txt        # Python dependencies
│
├── sql/
│   └── schema.sql          # SQLite schema + recursive closures
│
├── examples/
│   └── simple_kb.json      # sample knowledge base
│
├── schemas/
│   └── kb_schema.json      # JSON Schema for KB validation
│
└── tests/
    └── test_correctness.py # unit tests verifying inference correctness
```

### **Database Schema Overview (sql/schema.sql)**

Tables:

* `Class(sub, super)` — subclass axioms
* `Property(sub, super)` — subproperty axioms
* `Inverse(p, inv)` — inverse roles
* `Transitive(property)` — transitive roles
* `Domain(property, class)` / `Range(property, class)`
* `Type(individual, class)` — ABox typing
* `Rel(property, from_ind, to_ind)` — ABox relations

Recursive views:

* `ClassClosure` — subclass transitive closure
* `PropertyClosure` — subproperty transitive closure

SQLite’s `WITH RECURSIVE` implements closure-based reasoning.

---

## 4. Setup Instructions

### **Platform Requirements**

* Python **3.10+**
* SQLite (comes with Python’s `sqlite3` module)
* Confirmed working on **Windows 11** and Linux

### **Install Dependencies**

```
pip install -r requirements.txt
```

Dependencies:

* `jsonschema` — validates KB format
* `tabulate` — pretty-prints relations

---

## 5. Basic User Instructions (How to Run the System)

All commands run from the project root.

### **1. Initialize Database**

```
python dlp_fusion.py init
```

Creates SQLite tables and recursive views.

### **2. Load a Knowledge Base**

```
python dlp_fusion.py load examples/simple_kb.json
```

This:

1. Validates the KB JSON structure
2. Loads all TBox/ABox facts
3. Materializes inferences (inverse roles, transitivity, domain/range typing)

### **3. View Materialized Relations**

```
python dlp_fusion.py debug_rel
```

Example:

```
| property   | from   | to   |
|------------|--------|------|
| hasChild   | Mary   | Tom  |
| hasParent  | Tom    | Mary |
```

### **4. Query the Knowledge Base**

#### Instance checking

```
python dlp_fusion.py query type Tom Thing
```

#### Class subsumption

```
python dlp_fusion.py query sub Cat Thing
```

#### Subproperty subsumption

```
python dlp_fusion.py query subprop hasParent hasAncestor
```

---

## 6. Materialization Rules Implemented

1. **Inverse roles**: `Rel(p, x, y)` ⇒ `Rel(inv, y, x)`
2. **Transitive roles** via recursive SQL closure
3. **Domain typing**: `Rel(p, x, y)` + `Domain(p, C)` ⇒ `Type(x, C)`
4. **Range typing**: `Rel(p, x, y)` + `Range(p, C)` ⇒ `Type(y, C)`
5. **Instance checking** uses `Type` + `ClassClosure`

---

## 7. Testing

Run all unit tests:

```
python -m unittest discover -s tests
```

Tests verify:

* Direct type assertions
* Class hierarchy propagation
* Domain & range typing
* Inverse role inference
* Subclass & subproperty reasoning

---

## 8. Limitations & Future Work

* Only a small DHL fragment
* No cardinality constraints or complex role chains
* No justification/explanation tracing

Future extensions:

* Add explanation traces
* Expand DL constructors
* Import OWL/RDF subsets
* Benchmark larger ABoxes

---

## 9. Demo Script (Used for the Interview)

```
python dlp_fusion.py init
python dlp_fusion.py load examples/simple_kb.json
python dlp_fusion.py debug_rel

python dlp_fusion.py query type Tom Thing
python dlp_fusion.py query type Mary Animal
python dlp_fusion.py query sub Cat Thing
python dlp_fusion.py query subprop hasParent hasAncestor
```

This demonstrates complete system functionality: loading, inference, and DL-style querying.
