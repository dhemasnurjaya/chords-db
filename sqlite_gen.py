import sqlite3
import json
import os.path

db_output_path = "lib/guitar.db"

if os.path.exists(db_output_path):
    os.remove(db_output_path)

db = sqlite3.connect(db_output_path)
c = db.cursor()

create_table_queries = [
    """
    CREATE TABLE IF NOT EXISTS tunings(
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT,
        tuning  TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS keys (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS suffixes(
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS chords(
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        key         INTEGER,
        suffix      INTEGER,
        frets       TEXT,
        fingers     TEXT,
        base_fret   INTEGER,
        barres      TEXT,
        capo        INTEGER,
        midi        TEXT,
        FOREIGN KEY(key)    REFERENCES keys(id),
        FOREIGN KEY(suffix) REFERENCES suffixes(id)  
    );
    """,
]

for query in create_table_queries:
    c.execute(query)

db.commit()

f = open("lib/guitar.json")
guitar = json.load(f)
f.close()

for tuning in guitar["tunings"]:
    c.execute(
        "INSERT INTO tunings(name, tuning) VALUES (?, ?)",
        (
            tuning,
            ",".join(map(str, guitar["tunings"][tuning])),
        ),
    )

for key in guitar["keys"]:
    c.execute("INSERT INTO keys(name) VALUES (?)", (key,))

for suffix in guitar["suffixes"]:
    c.execute("INSERT INTO suffixes(name) VALUES (?)", (suffix,))

db.commit()

for chord_name in guitar["chords"]:
    chord_variations = guitar["chords"][chord_name]
    for chord in chord_variations:
        key_id = c.execute(
            "SELECT id FROM keys WHERE name = ?", (chord["key"],)
        ).fetchone()[0]

        suffix_id = c.execute(
            "SELECT id FROM suffixes WHERE name = ?", (chord["suffix"],)
        ).fetchone()[0]

        for position in chord["positions"]:
            c.execute(
                "INSERT INTO chords(key, suffix, frets, fingers, base_fret, barres, capo, midi) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    key_id,
                    suffix_id,
                    ",".join(map(str, position["frets"])),
                    ",".join(map(str, position["fingers"])),
                    position["baseFret"],
                    ",".join(map(str, position["barres"])),
                    int(position.get("capo", 0)),
                    ",".join(map(str, position["midi"])),
                ),
            )

    db.commit()

db.close()
