CREATE TABLE users (
    email TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    firstName TEXT NOT NULL,
    familyName TEXT NOT NULL,
    gender TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    message TEXT
);