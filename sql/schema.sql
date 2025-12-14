-- DLP-Fusion SQLite Schema

DROP TABLE IF EXISTS Class;
DROP TABLE IF EXISTS Property;
DROP TABLE IF EXISTS Transitive;
DROP TABLE IF EXISTS Inverse;
DROP TABLE IF EXISTS Domain;
DROP TABLE IF EXISTS Range;
DROP TABLE IF EXISTS Type;
DROP TABLE IF EXISTS Rel;

DROP VIEW IF EXISTS ClassClosure;
DROP VIEW IF EXISTS PropertyClosure;

-------------------------------
-- TBox Tables
-- -----------------------------

CREATE TABLE Class (
    sub TEXT NOT NULL,
    super TEXT NOT NULL,
    PRIMARY KEY (sub, super)
);

CREATE TABLE Property (
    sub TEXT NOT NULL,
    super TEXT NOT NULL,
    PRIMARY KEY (sub, super)
);

CREATE TABLE Transitive (
    property TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE Inverse (
    p TEXT NOT NULL,
    inv TEXT NOT NULL,
    PRIMARY KEY (p, inv)
);

CREATE TABLE Domain (
    property TEXT NOT NULL,
    class TEXT NOT NULL,
    PRIMARY KEY (property, class)
);

CREATE TABLE Range (
    property TEXT NOT NULL,
    class TEXT NOT NULL,
    PRIMARY KEY (property, class)
);

-- -----------------------------
-- ABox Tables
-- ---------------------------

CREATE TABLE Type (
    individual TEXT NOT NULL,
    class TEXT NOT NULL,
    PRIMARY KEY (individual, class)
);

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

CREATE INDEX idx_inv_p ON Inverse(p);
CREATE INDEX idx_dom_prop ON Domain(property);
CREATE INDEX idx_rng_prop ON Range(property);

-- -----------------------------
-- Recursive Closures
-- -----------------------------

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
