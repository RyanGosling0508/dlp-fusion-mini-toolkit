-- DLP-Fusion SQLite Schema
-- Week 1-2: Basic schema + recursive closures for DHL subset

-- Drop existing tables if they exist
DROP TABLE IF EXISTS Class;
DROP TABLE IF EXISTS Property;
DROP TABLE IF EXISTS Transitive;
DROP TABLE IF EXISTS Type;
DROP TABLE IF EXISTS Rel;

-- Drop closure views if they exist
DROP VIEW IF EXISTS ClassClosure;
DROP VIEW IF EXISTS PropertyClosure;

-- -----------------------------
-- TBox Tables
-- -----------------------------

-- Class hierarchy (subClassOf)
CREATE TABLE Class (
    sub TEXT NOT NULL,
    super TEXT NOT NULL,
    PRIMARY KEY (sub, super)
);

-- Property hierarchy (subPropertyOf)
CREATE TABLE Property (
    sub TEXT NOT NULL,
    super TEXT NOT NULL,
    PRIMARY KEY (sub, super)
);

-- Transitive properties
CREATE TABLE Transitive (
    property TEXT NOT NULL PRIMARY KEY
);

-- -----------------------------
-- ABox Tables
-- -----------------------------

-- Individual type assertions
CREATE TABLE Type (
    individual TEXT NOT NULL,
    class TEXT NOT NULL,
    PRIMARY KEY (individual, class)
);

-- Property assertions (relations)
CREATE TABLE Rel (
    property TEXT NOT NULL,
    from_ind TEXT NOT NULL,
    to_ind TEXT NOT NULL,
    PRIMARY KEY (property, from_ind, to_ind)
);

-- -----------------------------
-- Indexes
-- -----------------------------
CREATE INDEX idx_class_sub ON Class(sub);
CREATE INDEX idx_class_super ON Class(super);

CREATE INDEX idx_prop_sub ON Property(sub);
CREATE INDEX idx_prop_super ON Property(super);

CREATE INDEX idx_type_individual ON Type(individual);
CREATE INDEX idx_rel_property ON Rel(property);

-- -----------------------------
-- Recursive Closures (Week 2)
-- -----------------------------

-- ClassClosure: transitive closure of subClassOf
CREATE VIEW ClassClosure AS
WITH RECURSIVE closure(sub, super) AS (
    SELECT sub, super FROM Class
    UNION
    SELECT c.sub, p.super
    FROM Class AS c
    JOIN closure AS p
      ON c.super = p.sub
)
SELECT * FROM closure;

-- PropertyClosure: transitive closure of subPropertyOf
CREATE VIEW PropertyClosure AS
WITH RECURSIVE closure(sub, super) AS (
    SELECT sub, super FROM Property
    UNION
    SELECT p.sub, q.super
    FROM Property AS p
    JOIN closure AS q
      ON p.super = q.sub
)
SELECT * FROM closure;
