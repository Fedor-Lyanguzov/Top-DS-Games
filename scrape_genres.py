"""
### Сопоставление игр с жанрами

Необходимо для каждой игры из базового набора найти жанры на ее странице на metacritic. Создать таблицу жанров и соединить отношением многие-ко-многим с таблицей базового набора игр.
"""
import sqlite3
import requests
import lxml.html
import time
import traceback


def load_page(base_url, link):
    return requests.get(
        base_url + link,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"
        },
    ).text


def parse_page(page):
    """
    metascore:
    /html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[1]/div/div/a/div/span
    /html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/div/div/a/div/span
    /html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/div/div/a/div/span
    userscore:
    /html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div/a/div
    /html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div[1]/div[2]/div[1]/div/a/div
    genres:
    /html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div[3]/div/div[2]/div[2]/div[2]/ul/li[2]/span[@class="data"]

    """
    tree = lxml.html.fromstring(page)
    try:
        metascore = int(
            tree.xpath(
                "/html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div[3]//div[2]/div[1]/div[1]/div/div/a/div/span"
            )[0].text
        )
    except ValueError:
        metascore = None
    except IndexError:
        metascore = None
    try:
        userscore = int(
            float(
                tree.xpath(
                    "/html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div[3]//div[2]/div[1]/div[2]/div[1]/div/a/div"
                )[0].text
            )
            * 10
        )
    except ValueError:
        userscore = None
    except IndexError:
        print("Invalid xpath for userscore")
        raise
    genres = [
        x.text
        for x in tree.xpath(
            '/html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div[3]//div[2]/div[2]/div[2]/ul/li[2]/span[@class="data"]'
        )
    ]
    return metascore, userscore, genres


def update_score(db, game_id, metascore, userscore):
    db.execute(
        "UPDATE top_games SET metascore=?, userscore=? WHERE ROWID=?;",
        (metascore, userscore, game_id),
    )


def update_genres(db, genres):
    db.executemany("INSERT OR IGNORE INTO genres VALUES (?);", map(lambda x: (x,), genres))


def link_game_to_genres(db, game_id, genres):
    query = """
    INSERT INTO game_to_genre
    SELECT ?, genres.ROWID FROM genres
    WHERE genres.name=?;
    """
    db.executemany(query, map(lambda x: (game_id, x), set(genres)))


def load_pages(db, base_url):
    db.execute("DROP TABLE IF EXISTS games_pages;")
    db.execute("CREATE TABLE games_pages (id_game INTEGER UNIQUE, content TEXT);")
    for i, link in db.execute("SELECT ROWID, link FROM top_games ORDER BY ROWID;"):
        page = load_page(base_url, link)
        db.execute("INSERT INTO games_pages VALUES (?, ?);", (i, page))
        time.sleep(0.5)
        if i % 100 == 0:
            print(i)


def main(db_name, base_url):
    with sqlite3.connect(db_name) as db:
        db.execute("DROP TABLE IF EXISTS genres;")
        db.execute("DROP TABLE IF EXISTS game_to_genre;")
        db.execute("CREATE TABLE genres (name TEXT UNIQUE);")
        db.execute("CREATE TABLE game_to_genre (id_game INTEGER, id_genre INTEGER);")
        for i, name, link in db.execute("SELECT ROWID, name, link FROM top_games ORDER BY ROWID;"):
            (page,) = db.execute(
                "SELECT content FROM games_pages WHERE id_game=?;", (i,)
            ).fetchone()
            metascore, userscore, genres = parse_page(page)
            update_score(db, i, metascore, userscore)
            update_genres(db, genres)
            link_game_to_genres(db, i, genres)


def test_parse_page():
    with sqlite3.connect(db_name) as db:
        for i, link in db.execute("SELECT ROWID, link FROM top_games WHERE ROWID IN (1,2,3);"):
            page = load_page(base_url, link)
            metascore, userscore, genres = parse_page(page)
            print(metascore, userscore, genres)
    breakpoint()


def test_insert_not_unique():
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE genres (name TEXT UNIQUE);")
        genres = ["a", "b", "a", "b"]
        update_genres(db, genres)
        assert db.execute("SELECT ROWID, * FROM genres;").fetchall() == [(1, "a"), (2, "b")]
    breakpoint()


if __name__ == "__main__":
    db_name = "db.sqlite3"
    base_url = "https://www.metacritic.com"
    main(db_name, base_url)
