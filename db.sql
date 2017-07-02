CREATE TABLE users(
  id INT(10) AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  email VARCHAR(50),
  username VARCHAR(50),
  password VARCHAR(100),
  register_date TIMESTAMP
);

CREATE TABLE letter(
  id INT(10) AUTO_INCREMENT PRIMARY KEY,
  letra VARCHAR(50),
  frec NUMERIC(50)
);

INSERT INTO letter (letra, frec) VALUES ('A', 10);
INSERT INTO letter (letra, frec) VALUES ('B', 8);
INSERT INTO letter (letra, frec) VALUES ('C', 5);
INSERT INTO letter (letra, frec) VALUES ('D', 1);

DESCRIBE users;

SELECT * FROM letter;