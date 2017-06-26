CREATE TABLE users(
  id INT(10) AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  email VARCHAR(50),
  username VARCHAR(50),
  password VARCHAR(100),
  register_date TIMESTAMP
);

DESCRIBE users;