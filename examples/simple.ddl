-- Create the 'Companies' table
CREATE TABLE Pokemon (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    type1 VARCHAR(20) NOT NULL,
    type2 VARCHAR(20),
    hp INT,
    attack INT,
    defense INT,
    speed INT
);