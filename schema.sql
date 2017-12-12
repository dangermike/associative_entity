DROP DATABASE IF EXISTS assoc_test;
CREATE DATABASE assoc_test;
USE assoc_test;

DROP TABLE IF EXISTS people_companies_id;
DROP TABLE IF EXISTS people_companies;
DROP TABLE IF EXISTS people;
DROP TABLE IF EXISTS companies;

CREATE TABLE people (
	id int NOT NULL PRIMARY KEY,
	name varchar(50) NOT NULL,
	UNIQUE KEY ix_people__name (name)
);

CREATE TABLE companies (
	id int NOT NULL PRIMARY KEY,
	name varchar(50) NOT NULL,
	UNIQUE KEY ix_companies__name (name)

);

CREATE TABLE people_companies (
  p_id int NOT NULL,
  c_id int NOT NULL,
  CONSTRAINT people_companies PRIMARY KEY (p_id, c_id),
  KEY ix_people_companies__c_id (c_id),
  CONSTRAINT fk_people_companies__people FOREIGN KEY (p_id) REFERENCES people (id),
  CONSTRAINT fk_people_companies__companies FOREIGN KEY (c_id) REFERENCES companies (id)
);

CREATE TABLE people_companies_id (
  id int NOT NULL PRIMARY KEY,
  p_id int NOT NULL,
  c_id int NOT NULL,
  UNIQUE KEY ix_people_companies_id___p_id__c_id (p_id, c_id),
  KEY ix_people_companies_id___c_id (c_id),
  CONSTRAINT fk_people_companies_id__people FOREIGN KEY (p_id) REFERENCES people (id),
  CONSTRAINT fk_people_companies_id__companies FOREIGN KEY (c_id) REFERENCES companies (id)
);