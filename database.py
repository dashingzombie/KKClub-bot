import sqlite3
from datetime import datetime
import time

class Database():

    def __init__(self, database_name: str ):
        self.conn = sqlite3.connect(database_name)
        self.cur = self.conn.cursor()



    def check_user(self, username_id):
        t = (username_id,)
        self.cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", t)
        users = self.cur.fetchall()
        if (users[0][0] == 0):
            return False
        else:
            return True

    def add_user(self, username_id):
        t = (username_id, 0,)
        self.cur.execute("INSERT INTO users(username, points) VALUES(?,?)", t)
        self.conn.commit()

    def add_points_user(self,username_id, points):
        t = (points, username_id,)
        self.cur.execute("UPDATE users SET points = points + ? WHERE username = ?", t)
        self.conn.commit()

    def remove_points(self,username_id, points):
        t = (points, username_id,)
        t2 = (username_id,)
        self.cur.execute("UPDATE users SET points = points - ? WHERE username = ?", t)
        self.cur.execute("UPDATE users SET points = 0 WHERE username = ? AND points < 0", t2)
        self.conn.commit()

    def add_points(self,username_id, points):
        t = (username_id,)
        if (self.check_user(username_id) == False and username_id.isdigit()):
            self.add_user(username_id)
            self.add_points_user(username_id, points)
        elif (username_id.isdigit()):
            self.add_points_user(username_id, points)

    def add_leaderboard(self,username, message_id, count):
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        t = (username, message_id, timestamp, 1, count,)
        self.cur.execute(
            "INSERT INTO board_tables(username, message_id, created_time, page_number, last_usernumber) VALUES(?,?,?,?,?)",
            t)
        self.conn.commit()

    def check_leaderboard(self,message_id, user_id):

        t = (user_id, message_id,)
        self.cur.execute("SELECT COUNT(*) FROM board_tables WHERE username = ? AND message_id = ?", t)
        data = self.cur.fetchall()
        if (data[0][0] == 0):
            return False
        else:
            return True

    def get_user_point(self,username_id):

        t = (username_id,)
        self.cur.execute("SELECT * FROM users WHERE username = ?", t)
        data = self.cur.fetchall()
        if not data:
            return 0
        else:
            return data[0][2]

    def get_leaderboard_page(self,message_id, user_id):

        t = (user_id, message_id,)
        self.cur.execute("SELECT * FROM board_tables WHERE username = ? AND message_id = ?", t)
        data = self.cur.fetchall()
        return data[0][4], data[0][5]

    def update_leaderboard(self,page, last_user, message_id):

        t = (page, last_user, message_id)
        self.cur.execute("UPDATE board_tables SET page_number = ? , last_usernumber = ? WHERE message_id = ?", t)
        self.conn.commit()

    def get_users(self,page=1):
        page_offset = (page - 1) * 10
        self.cur.execute("SELECT * FROM users ORDER BY points DESC LIMIT " + str(page_offset) + ",10")
        rows = self.cur.fetchall()
        return rows

    def insert_points_requests(self,message_id, users, points, approved, created_by):
        t = (message_id, users, points, approved, created_by,)
        self.cur.execute("INSERT INTO points_requests(message_id, users, points, approved, created_by)  VALUES(?,?,?,?,?)",
                    t)
        self.conn.commit()

    def check_requests(self,message_id):

        t = (message_id,)
        self.cur.execute("SELECT * FROM points_requests WHERE message_id = ? AND approved = 0 LIMIT 1", t)
        data = self.cur.fetchall()
        if (not data):
            return None
        else:
            return True

    def get_users_requests(self,message_id):

        t = (message_id,)
        self.cur.execute("SELECT * FROM points_requests WHERE message_id = ? LIMIT 1", t)
        data = self.cur.fetchall()
        if (not data):
            return None
        else:
            return data[0][2], data[0][3]

    def update_requests(self,message_id, app):
        t = (app, message_id,)
        self.cur.execute("UPDATE points_requests SET approved = ? WHERE message_id = ?", t)
        self.conn.commit()

    async def reset_database(self):
        self.cur.execute("DELETE FROM users WHERE 'a' = 'a'")
        self.conn.commit()
