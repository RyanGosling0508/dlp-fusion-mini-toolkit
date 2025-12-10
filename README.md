# DLP-Fusion Mini-Toolkit

### CSE498-46 Knowledge Representation

### Yutong Chen

DLP-Fusion is a small reasoning toolkit that translates a **DHL subset** of
Description Logic into a Datalog-style rule engine on top of **SQLite**.

It supports:

* Loading a lightweight JSON knowledge base (KB)
* Translating a DHL fragment into relational tables
* Materializing inferences using SQL rules
* Answering DL-style queries (`type`, `sub`, `subprop`) via a simple CLI

The project is inspired by the paper:

> Grosof et al., **"Description Logic Programs: Combining Logic Programs with
> Description Logics"**, WWW 2003.

---

## 1. DHL Fragment Supported

The toolkit focuses on a small, Horn-style DHL fragment with:

### TBox constructs

* `subClassOf(C, D)` – subclass axioms
* `subPropertyOf(R, S)` – subproperty axioms
* `inverseOf(R, S)` – inverse roles
* `domain(R, C)` – domain typing
* `range(R, C)` – range typing
* `transitiveProperty(R)` – transitive roles

### ABox assertions

* `Type(a, C)` – individual `a` is instance of class `C`
* `Rel(R, a, b)` – role `R` holds between `a` and `b`

This is expressive enough to illustrate the DLP-style intersection between
Description Logics and Logic Programming without a heavy OWL reasoner.

---

## 2. Architecture & File Structure

Project layout (simplified):

```
project/
│
├── dlp_fusion.py           # main engine + CLI
├── requirements.txt        # Python dependencies
│
├── sql/
│   └── schema.sql          # SQLite schema + recursive closure views
│
├── examples/
│   └── simple_kb.json      # example DHL knowledge base
│
├── schemas/
│   └── kb_schema.json      # JSON Schema for KB validation
│
└── tests/
    └── test_correctness.py # unit tests for core reasoning features
```

### SQLite schema (`sql/schema.sql`)

Main tables:

* `Class(sub, super)` – subclass axioms
* `Property(sub, super)` – subproperty axioms
* `Transitive(property)` – transitive roles
* `Inverse(p, inv)` – inverse roles
* `Domain(property, class)` – domain typing
* `Range(property, class)` – range typing
* `Type(individual, class)` – ABox types
* `Rel(property, from_ind, to_ind)` – ABox role assertions

Recursive closure views:

* `ClassClosure(sub, super)`
* `PropertyClosure(sub, super)`

Both use `WITH RECURSIVE` to compute transitive closure.

---

## 3. JSON KB Format

Example: `examples/simple_kb.json` (simplified):

```json
{
  "tbox": {
    "classes": ["Thing", "LivingThing", "Animal", "Human", "Cat", "Dog"],
    "properties": ["hasParent", "hasAncestor", "hasChild", "ownsPet"],

    "subClassOf": [
      { "sub": "LivingThing", "super": "Thing" },
      { "sub": "Animal", "super": "LivingThing" },
      { "sub": "Human", "super": "Animal" },
      { "sub": "Cat", "super": "Animal" },
      { "sub": "Dog", "super": "Animal" }
    ],

    "subPropertyOf": [
      { "sub": "hasParent", "super": "hasAncestor" }
    ],

    "inverseOf": [
      { "p": "hasParent", "inv": "hasChild" }
    ],

    "transitiveProperty": [
      "hasAncestor"
    ],

    "domain": [
      { "property": "hasParent", "class": "Animal" }
    ],

    "range": [
      { "property": "hasParent", "class": "Animal" }
    ]
  },

  "abox": {
    "individuals": ["Tom", "Mary", "Fluffy", "Rex"],

    "types": [
      { "individual": "Tom", "class": "Human" },
      { "individual": "Fluffy", "class": "Cat" }
    ],

    "relations": [
      { "property": "hasParent", "from": "Tom", "to": "Mary" }
    ]
  }
}
```

The KB is validated against `schemas/kb_schema.json` using `jsonschema`. If the schema
file is missing, validation is skipped with a warning.

---

## 4. Setup Instructions

### Requirements

* **Python** ≥ 3.10
* **SQLite** (standard Python `sqlite3` module)
* OS: tested on Windows 11 and Linux, but should run on any OS with Python 3.

### Install dependencies

```bash
pip install -r requirements.txt
```

Dependencies include:

* `jsonschema` – for KB validation
* `tabulate` – for pretty-printing the materialized `Rel` table

---

## 5. CLI Usage

All commands are run from the project root.

### 1. Initialize the database

```bash
python dlp_fusion.py init
```

### 2. Load a knowledge base

```bash
python dlp_fusion.py load examples/simple_kb.json
```

This:

1. Validates the JSON
2. Inserts TBox + ABox facts
3. Materializes inferences

### 3. Inspect materialized relations

```bash
python dlp_fusion.py debug_rel
```

Example:

```
| property   | from   | to   |
|------------|--------|------|
| hasChild   | Mary   | Tom  |
| hasParent  | Tom    | Mary |
```

### 4. Queries

#### Instance checking

```bash
python dlp_fusion.py query type Tom Thing
```

#### Class subsumption

```bash
python dlp_fusion.py query sub Cat Thing
```

#### Subproperty subsumption

```bash
python dlp_fusion.py query subprop hasParent hasAncestor
```

---

## 6. Materialization Rules

1. **Inverse roles** — `Rel(p, x, y)` ⇒ `Rel(inv, y, x)`
2. **Transitive roles** — recursive SQL closure
3. **Domain typing** — `Rel(p, x, y)` + `domain(p, C)` ⇒ `Type(x, C)`
4. **Range typing** — `Rel(p, x, y)` + `range(p, C)` ⇒ `Type(y, C)`

Instance checking uses `Type` + `ClassClosure`.

---

## 7. Testing

Run all tests:

```bash
python -m unittest discover -s tests
```

Covers:

* Direct types
* Class hierarchy typing
* Domain & range typing
* Inverse role expansion
* Subclass & subproperty queries

---

## 8. Limitations & Future Work

* Only a small DHL fragment is supported
* No cardinality, nominals, complex role chains
* No explanation traces

Possible extensions:

* More DL constructors
* Proof explanation
* Performance experiments
* Importing OWL/RDF subsets

---

## 9. Demo Script

```
python dlp_fusion.py init
python dlp_fusion.py load examples/simple_kb.json
python dlp_fusion.py debug_rel

python dlp_fusion.py query type Tom Thing
python dlp_fusion.py query type Mary Animal
python dlp_fusion.py query sub Cat Thing
python dlp_fusion.py query subprop hasParent hasAncestor
```

This demonstrates loading, inference materialization, and DL-style queries.
