CREATE TABLE preferunits (
  userName VARCHAR(50) NOT NULL,
  unitName VARCHAR(255) NOT NULL,
  unitType VARCHAR(255) NOT NULL,
  PRIMARY KEY (userName, unitType));