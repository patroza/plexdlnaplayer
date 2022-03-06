import sqlite3

con = sqlite3.connect('./db/com.plexapp.dlna.db')


def get_id(id):
  cur = con.cursor()
  q = 'SELECT * FROM object_ids WHERE plex_path = \'' + str(id) + '\''
  print(q)
  cur.execute(q)
  return cur.fetchone()[0]



if __name__ == "__main__":
    print(get_id('/library/metadata/3603'))
