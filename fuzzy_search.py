
import sqlite3
from ngram import NGram

tr_table = str.maketrans('','',' !$&\'()+,-.=@[]')

def key(s):
    """
     !$&'()+,-.0123456789=@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]abcdefghijklmnopqrstuvwxyz
    """
    return s.removesuffix('.zip').lower().translate(tr_table)

def test_key():
    """
    1 vs 100 (Europe) [b].zip
    1 vs 100 (europe) [b]
    """
    s = '1 vs 100 (Europe) [b].zip'
    assert key(s) == '1vs100europeb', key('1 vs 100 (Europe) [b].zip') 

def select(name, xs):
    while True:
        print(f'?: {name}')
        for i, ((_, name), _) in enumerate(xs,1):
            print(f'{i}. {name}')
        inp = input('1-9,n: ')
        if inp=='':
            return xs[0]
        if inp=='n':
            raise ValueError
        if inp in set('123456789'):
            return xs[int(inp)-1]

if __name__=='__main__':
    test_key()
    with sqlite3.connect("db.sqlite3") as db:
        G = NGram(key=lambda x: key(x[1]))
        for game in db.execute("SELECT ROWID, zip_name FROM archive;"):
            G.add(game)

        db.execute("DROP TABLE IF EXISTS game_to_archive;")
        db.execute("CREATE TABLE game_to_archive (id_game INTEGER, id_archive INTEGER);")
        for id_game, name in db.execute("SELECT ROWID, name FROM top_games;"):
            try:
                ((id_a1, n1), p1), ((id_a2, n2), p2) = G.search(name)[:2]
                if p1/p2<1.05:
                    (id_a1, n1), p1 = select(name, G.search(name)[:9])
                db.execute("INSERT INTO game_to_archive VALUES (?, ?);", (id_game, id_a1))
            except:
                db.execute("INSERT INTO game_to_archive VALUES (?, NULL);", (id_game,))
            
