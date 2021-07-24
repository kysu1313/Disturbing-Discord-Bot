import os
import datetime
import pyodbc
import time

STARTING_MONEY = 500

class DbConn:
    def __init__(self):
        self.host = os.environ.get('DB_HOST')
        self.username = os.environ.get('DB_USERNAME')
        self.password = os.environ.get('DB_PASSWORD')
        self.dbName = os.environ.get('DB_NAME')
        self.driver = '{ODBC Driver 17 for SQL Server}'
        self.conn = None

    def __connect(self):

        self.conn = pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.host+';PORT=1433;DATABASE='+self.dbName+';UID='+self.username+';PWD='+ self.password)
        return self.conn

        #with pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.server+';PORT=1433;DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password) as conn:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT TOP 3 name, collation_name FROM sys.databases;")
                row = cursor.fetchone()
                while row:
                    print (str(row[0]) + " " + str(row[1]))
                    row = cursor.fetchone()

    
    def add_server(self, server_id, server_name):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.ServerTable WHERE server_id={};".format(server_id))
                server = cursor.fetchone()
                if server is None:
                    cursor.execute("INSERT INTO dbo.ServerTable (server_id, server_name) VALUES (?, ?);", server_id, server_name)

    def add_user(self, user_id, server_id, wallet, bank, username):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    self.__insert_user(user_id, server_id, wallet, bank)
                    return True
                return False

    def __insert_user(self, user_id, server_id, wallet, bank):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO dbo.Users (user_id, username) VALUES (?, ?);", user_id, username)
                cursor.execute(
                    """
                        INSERT INTO dbo.UserExperience (server_id, user_id, bank, wallet, messages, userLevel, experience, emojiSent, reactionsReceived, dateUpdated) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, user_id, server_id, bank, wallet, 0, 0, 0, 0, 0, time.datetime.now)
                return

    def get_user(self, user_id, server_id):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.UserExperience WHERE user_id={} AND server_id={};".format(user_id, server_id))
                user = cursor.fetchone()
                return user
        return None

    def get_server(self, server_id):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.ServerTable WHERE server_id={};".format(server_id))
                server = cursor.fetchone()
                return server
        return None
        
    def get_all_servers(self):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.ServerTable")
                servers = cursor.fetchall()
                return servers
        return None

    def update_user_money(self, user_id, server_id, wallet, bank):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    self.__insert_user(user_id, server_id, wallet, bank)
                    return
                else:
                    cursor.execute(
                        """
                            UPDATE dbo.UserExperience 
                            SET bank=?, wallet=?
                            WHERE user_id=? and server_id=?
                        """, bank, wallet, user_id, server_id)
                    return

    def update_user_messages(self, user_id, server_id, messages):
        global STARTING_MONEY
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    self.__insert_user(user_id, server_id, STARTING_MONEY, STARTING_MONEY)
                    return
                else:
                    cursor.execute(
                        """
                            UPDATE dbo.UserExperience 
                            SET messages=?
                            WHERE user_id=? and server_id=?
                        """, messages, user_id, server_id)
                    return

    def update_user_level(self, user_id, server_id, level):
        global STARTING_MONEY
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    self.__insert_user(user_id, server_id, STARTING_MONEY, STARTING_MONEY)
                    return
                else:
                    cursor.execute(
                        """
                            UPDATE dbo.UserExperience 
                            SET userLevel=?
                            WHERE user_id=? and server_id=?
                        """, level, user_id, server_id)
                    return

    def update_user_experience(self, user_id, server_id, experience):
        global STARTING_MONEY
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    self.__insert_user(user_id, server_id, STARTING_MONEY, STARTING_MONEY)
                    return
                else:
                    cursor.execute(
                        """
                            UPDATE dbo.UserExperience 
                            SET experience=?
                            WHERE user_id=? and server_id=?
                        """, experience, user_id, server_id)
                    return

    def update_user_emoji_sent(self, user_id, server_id, emojis):
        global STARTING_MONEY
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    self.__insert_user(user_id, server_id, STARTING_MONEY, STARTING_MONEY)
                    return
                else:
                    cursor.execute(
                        """
                            UPDATE dbo.UserExperience 
                            SET emojiSent=?
                            WHERE user_id=? and server_id=?
                        """, emojis, user_id, server_id)
                    return

    def update_user_emoji_sent(self, user_id, server_id, reactions_received):
        global STARTING_MONEY
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    self.__insert_user(user_id, server_id, STARTING_MONEY, STARTING_MONEY)
                    return
                else:
                    cursor.execute(
                        """
                            UPDATE dbo.UserExperience 
                            SET reactionsReceived=?
                            WHERE user_id=? and server_id=?
                        """, reactions_received, user_id, server_id)
                    return

    def update_user_updated_date(self, user_id, server_id, updated_date):
        global STARTING_MONEY
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    self.__insert_user(user_id, server_id, STARTING_MONEY, STARTING_MONEY)
                    return
                else:
                    cursor.execute(
                        """
                            UPDATE dbo.UserExperience 
                            SET updatedDate=?
                            WHERE user_id=? and server_id=?
                        """, updated_date, user_id, server_id)
                    return

    def update_user_values(self, user_id, server_id, bank, wallet, messages, userLevel, experience, emojiSent, reactionsReceived, dateUpdated):
        global STARTING_MONEY
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    self.__insert_user(user_id, server_id, STARTING_MONEY, STARTING_MONEY)
                    return
                else:
                    cursor.execute(
                        """
                            UPDATE dbo.UserExperience 
                            SET bank=?, wallet=?, messages=?, userLevel=?, experience=?, emojiSent=?, reactionsReceived=?, updatedDate=?
                            WHERE user_id=? and server_id=?
                        """, bank, wallet, messages, userLevel, experience, emojiSent, reactionsReceived, dateUpdated, user_id, server_id)
                    return

    def get_users_by_server(self, server_id):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.UserExperience WHERE server_id={};".format(server_id))
                users = cursor.fetchall()
                return users
        return None
        
    def get_user_in_server(self, user_id, server_id):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.UserExperience WHERE user_id={} AND server_id={};".format(user_id, server_id))
                user = cursor.fetchone()
                return user
        return None
        
    def insert_crypto(self, coin_name, price):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO dbo.cryptoPrices (coinName, price, midPrice, olderPrice, oldestPrice) VALUES (?, ?, ?, ?, ?);", coin_name, price, price, price, price)
                cursor.execute("SELECT * FROM dbo.cryptoPrices WHERE coinName=?", coin_name)
                coin = cursor.fetchone()
                return coin

    def get_and_update_crypto(self, coin_name, new_price):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.cryptoPrices WHERE coinName=?", coin_name)
                coin = cursor.fetchone()
                cursor.execute("UPDATE dbo.cryptoPrices SET price=?, midPrice=?, olderPrice=?, oldestPrice=?  WHERE coinName=?", new_price, coin.price, coin.midPrice, coin.olderPrice, coin_name)
                return coin
        
    def get_crypto(self, coin_name):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("SELECT * FROM dbo.cryptoPrices WHERE coinName=?", coin_name)
                    coin = cursor.fetchone()
                    return coin
                except Exception as e:
                    return None
        
        
    def add_member(self, server_id, user_id, username, ):
        conn = self.__connect()

if __name__ == '__main__':
    con = DbConn()
    #con.connect()
    con.add_server(861051867249639456, "Kyyysserver")
