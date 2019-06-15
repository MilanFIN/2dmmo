create table mmo (
    name VARCHAR (50) UNIQUE NOT NULL PRIMARY KEY,
    password VARCHAR (50) NOT NULL,
	gamestate jsonb NOT NULL
);
