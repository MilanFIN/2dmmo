create table mmo (
    name VARCHAR (50) UNIQUE NOT NULL PRIMARY KEY,
    password VARCHAR (80) NOT NULL,
	gamestate jsonb NOT NULL
);
GRANT ALL PRIVILEGES ON TABLE mmo TO mmo;
