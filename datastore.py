import mariadb

class DataStore:
  def __init__(self):
    self.conn = mariadb.connect(
      user="app",
      password="apppw",
      host="127.0.0.1",
      port=3306,
      database="app"
    )

    self.create_tables()

  def create_tables(self):
    cur = self.conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), keystone_password VARCHAR(255))")
    self.conn.commit()

  def add_user(self, username, password, keystone_password=None):
    cur = self.conn.cursor()
    cur.execute("INSERT INTO users (username, password, keystone_password) VALUES (?, ?, ?)", (username, password, keystone_password))
    self.conn.commit()

  def get_user(self, username):
    cur = self.conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cur.fetchone()