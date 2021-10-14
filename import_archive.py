import csv
import sqlite3


with sqlite3.connect("db.sqlite3") as db:
    db.execute("DROP TABLE IF EXISTS archive;")
    db.execute("CREATE TABLE archive (zip_name TEXT, nds_name TEXT, size INTEGER);")
    with open("archive.csv") as inp:
        reader = csv.reader(inp)
        db.executemany("INSERT INTO archive VALUES (?, ?, ?);", reader)
