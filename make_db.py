import sqlite3
import os
import os.path
import requests
import lxml.html


def load_pages(db, pages):
    db.execute("DROP TABLE IF EXISTS pages;")
    db.execute("CREATE TABLE pages (link TEXT UNIQUE, type TEXT, n INTEGER, content TEXT);")

    for by, p in pages.items():
        for i, x in enumerate(p):
            doc = requests.get(
                x,
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"
                },
            )
            db.execute("INSERT INTO pages VALUES (?, ?, ?, ?);", (x, by, i, doc.text))
    db.commit()


def process_pages(db):
    db.execute("DROP TABLE IF EXISTS top_games;")
    db.execute(
        "CREATE TABLE top_games (name TEXT, link TEXT UNIQUE, metascore INTEGER, userscore INTEGER);"
    )

    types = {
        "by_metascore": (
            """
            INSERT INTO top_games(name, link, metascore) 
            VALUES (?, ?, ?) 
            ON CONFLICT(link) DO 
            UPDATE SET metascore=excluded.metascore;
            """,
            int,
        ),
        "by_userscore": (
            """
            INSERT INTO top_games(name, link, userscore) 
            VALUES (?, ?, ?) 
            ON CONFLICT(link) DO 
            UPDATE SET userscore=excluded.userscore;
            """,
            lambda x: int(float(x) * 10),
        ),
    }
    for type, page in db.execute("SELECT type, content FROM pages;"):
        for tr in get_all_table_rows(page):
            query, score_converter = types[type]
            name, link, score = extract_data(tr, score_converter)
            db.execute(query, (name, link, score))
    db.commit()


def get_all_table_rows(page):
    """
    (1, 1): /html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[2]/table/tr[1]
    (1, 2): /html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[2]/table/tr[3]
    (2, 1): /html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[4]/table/tr[1]
    (3, 1): /html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[6]/table/tr[1]
    (4, 1): /html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[7]/table/tr[1]
    """
    tree = lxml.html.fromstring(page)
    tables = [
        "/html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[2]/table",
        "/html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[2]/table",
        "/html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[4]/table",
        "/html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[6]/table",
        "/html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[7]/table",
    ]
    for t in tables:
        table = tree.xpath(t)[0].getchildren()[::2]
        for tr in table:
            yield tr


def extract_data(tr, score_converter):
    """
    name:  /html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[2]/table/tr[1]/td[2]/a/h3
    link:  /html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[2]/table/tr[1]/td[2]/a
    score: /html/body/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div[2]/table/tr[1]/td[2]/div[1]/a/div
    """
    name = tr.xpath("td[2]/a/h3")[0].text
    link = tr.xpath("td[2]/a")[0].get("href")
    score = score_converter(tr.xpath("td[2]/div[1]/a/div")[0].text)
    return name, link, score


def clear_cache(args):
    return True


def parse_args():
    return None


def remove_db(db_filename):
    if db_exists(db_filename):
        os.remove(db_filename)


def db_exists(db_filename):
    return os.path.exists(db_filename)


def prepare_db(db_filename, pages):
    with sqlite3.connect(db_filename) as db:
        load_pages(db, pages)
        process_pages(db)


def main():
    db_filename = "db.sqlite3"
    pages = {
        "by_metascore": [
            "https://www.metacritic.com/browse/games/release-date/available/ds/metascore",
            "https://www.metacritic.com/browse/games/release-date/available/ds/metascore?page=1",
            "https://www.metacritic.com/browse/games/release-date/available/ds/metascore?page=2",
        ],
        "by_userscore": [
            "https://www.metacritic.com/browse/games/release-date/available/ds/userscore",
            "https://www.metacritic.com/browse/games/release-date/available/ds/userscore?page=1",
            "https://www.metacritic.com/browse/games/release-date/available/ds/userscore?page=2",
        ],
    }
    args = parse_args()
    if clear_cache(args):
        remove_db(db_filename)
    if not db_exists(db_filename):
        prepare_db(db_filename, pages)
    with sqlite3.connect(db_filename) as db:
        pass


if __name__ == "__main__":
    main()
