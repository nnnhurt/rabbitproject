
CREATE KEYSPACE IF NOT EXISTS my_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};

USE my_keyspace;

CREATE TABLE IF NOT EXISTS my_table1 (
    message text PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS my_table2 (
    message text PRIMARY KEY
);