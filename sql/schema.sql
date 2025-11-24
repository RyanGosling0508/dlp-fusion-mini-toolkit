-- DLP-Fusion SQLite Schema
-- Week 1: Basic schema for DHL subset

-- Drop existing tables if they exist
DROP TABLE IF EXISTS Class;
DROP TABLE IF EXISTS Property;
DROP TABLE IF EXISTS Transitive;
DROP TABLE IF EXISTS Type;
DROP TABLE IF EXISTS Rel;

-- TBox Tables

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

-- ABox Tables

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

-- Create indexes for better performance
CREATE INDEX idx_class_sub ON Class(sub);
CREATE INDEX idx_class_super ON Class(super);
CREATE INDEX idx_type_individual ON Type(individual);
CREATE INDEX idx_rel_property ON Rel(property);