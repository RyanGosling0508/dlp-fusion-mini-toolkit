# DLP-Fusion Mini-Toolkit

A lightweight reasoning toolkit that translates a DHL subset of Description Logic (DL) into a Datalog/SQLite-style rule system. The system loads knowledge bases in JSON format, materializes logical inferences inside SQLite, and supports DL-style instance and subsumption queries via a simple CLI.

---

## **1. Features (Weeks 1–3 Completed)**

### ✅ **Lightweight JSON DHL Subset Parser**

Supports TBox and ABox structures:

* `subClassOf`
* `subPropertyOf`
* `inverseOf`
* `domain`
* `range`
* `transitiveProperty`
* `types`
* `relations`

### ✅ **SQLite Schema for DL/Horn Mapping**

Implements tables:

* `Class(sub, super)`
* `Property(sub, super)`
* `Transitive(property)`
* `Inverse(p, inv)`
* `Domain(property, class)`
* `Range(property, class)`
* `Type(individual, class)`
* `Rel(property, from_ind, to_ind)`

Includes optimized indexes for query performance.

### ✅ **Recursive Closures Using WITH RECURSIVE**

* `ClassClosure` — transitive closure of subclass hierarchy.
* `PropertyClosure` — transitive closure of subproperty hierarchy.

Enables queries like:

```
query sub Cat Thing → True
query subprop hasParent hasAncestor → True
```

### ✅ **Materialized Reasoning (Week 3)**

At KB load time, the system automatically computes:

* **Inverse roles**: `Rel(p, x, y) → Rel(inv, y, x)`
* **Domain typing**: `Rel(p, x, y) & domain(p, C) → Type(x, C)`
* **Range typing**: `Rel(p, x, y) & range(p, C) → Type(y, C)`
* **Transitive role closure** for properties listed in `transitiveProperty`

Example inferred facts:

```
Type(Tom, Animal)   # via domain rule
Type(Mary, Animal)  # via range rule
Rel(hasChild, Mary, Tom)  # via inverseOf
```

### ✅ **CLI Query Engine**

```
python dlp_fusion.py init
python dlp_fusion.py load examples/simple_kb.json
python dlp_fusion.py query type Tom Human
python dlp_fusion.py query sub Cat Thing
python dlp_fusion.py query subprop hasParent hasAncestor
```

---

## **2. File Structure**

```
project/
│   dlp_fusion.py
│   README.md
│
├── sql/
│   └── schema.sql
│
├── examples/
│   └── simple_kb.json
│
└── tests/
    └── test_correctness.py (Week 4)
```

---

## **3. Installation & Setup**

### **Create Environment**

```
conda create -n dlp_fusion python=3.11 -y
conda activate dlp_fusion
```

### **Run Initialization**

```
python dlp_fusion.py init
```

### **Load Knowledge Base**

```
python dlp_fusion.py load examples/simple_kb.json
```

---

## **4. Query Usage**

### **Instance Checking**

```
python dlp_fusion.py query type Tom Animal
```

### **Subclass Checking**

```
python dlp_fusion.py query sub Cat Thing
```

### **Subproperty Checking**

```
python dlp_fusion.py query subprop hasParent hasAncestor
```

---

## **5. Example KB (simple_kb.json)**

A compact ontology demonstrating:

* subclass hierarchy
* property hierarchy
* inverse roles
* domain/range typing
* transitive roles

```json
{
  "tbox": {
    "classes": ["Thing", "LivingThing", "Animal", "Human", "Cat", "Dog"],
    "properties": ["hasParent", "hasAncestor", "hasChild", "ownsPet"],

    "subClassOf": [
      {"sub": "LivingThing", "super": "Thing"},
      {"sub": "Animal", "super": "LivingThing"},
      {"sub": "Human", "super": "Animal"},
      {"sub": "Cat", "super": "Animal"},
      {"sub": "Dog", "super": "Animal"}
    ],

    "subPropertyOf": [
      {"sub": "hasParent", "super": "hasAncestor"}
    ],

    "inverseOf": [
      {"p": "hasParent", "inv": "hasChild"}
    ],

    "domain": [
      {"property": "hasParent", "class": "Animal"}
    ],

    "range": [
      {"property": "hasParent", "class": "Animal"}
    ],

    "transitiveProperty": ["hasAncestor"]
  },

  "abox": {
    "types": [
      {"individual": "Tom", "class": "Human"},
      {"individual": "Fluffy", "class": "Cat"}
    ],

    "relations": [
      {"property": "hasParent", "from": "Tom", "to": "Mary"}
    ]
  }
}
```

---

## **6. Progress Summary (Weeks 1–3)**

### **Week 1 – Foundations**

* Created Conda environment & VS Code setup
* Designed JSON schema and SQLite schema
* Implemented base CLI (`init`, `load`)
* Added simple KB for testing

### **Week 2 – Core Reasoning Infrastructure**

* Implemented full JSON loader
* Added recursive SQL: `ClassClosure`, `PropertyClosure`
* Added subsumption and subproperty queries
* Verified closure correctness with sample KB

### **Week 3 – Materialized Logical Rules**

* Implemented inverseOf, domain, range rules
* Implemented transitive role closure
* Integrated inference into load-time materialization
* Verified all rules using updated KB examples

System now supports complete subclass/property closure + core DHL reasoning.

---

## **7. Next Steps (Week 4+)**

* Build correctness test suite (unittest)
* Add reasoning chain explanation (optional)
* Add performance evaluation scripts
* Prepare final demo and report

---

Ready for extension into full DHL/Datalog hybrid reasoning.
