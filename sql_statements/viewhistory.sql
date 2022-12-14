CREATE TABLE viewhistory (
  userName VARCHAR(50) NOT NULL,
  recipeID INT NOT NULL,
  timestamp TIMESTAMP NULL,
  PRIMARY KEY (userName, recipeID));
DROP TRIGGER IF EXISTS viewhistory_BEFORE_INSERT;

DELIMITER $$
CREATE DEFINER = CURRENT_USER TRIGGER viewhistory_BEFORE_INSERT BEFORE INSERT ON viewhistory FOR EACH ROW
BEGIN
set new.timestamp = current_timestamp();
END$$
DELIMITER ;
