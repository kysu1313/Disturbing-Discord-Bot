import os
import datetime
import pyodbc

# ServerTable
# Users

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
                    cursor.execute("INSERT INTO dbo.Users (user_id, server_id, wallet, bank, username) VALUES (?, ?, ?, ?, ?);", user_id, server_id, wallet, bank, username)
                    return True
                return False
                    
    def get_user(self, user_id):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
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

    def update_user_money(self, user_id, server_id, wallet, bank, username):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={};".format(user_id))
                user = cursor.fetchone()
                if user is None:
                    cursor.execute("INSERT INTO dbo.Users (user_id, server_id, wallet, bank, username) VALUES (?, ?, ?, ?, ?);", user_id, server_id, wallet, bank, username)
                    return True
                else:
                    cursor.execute("UPDATE dbo.Users SET bank=?, wallet=? WHERE user_id=?", bank, wallet, user_id)
                    return True
                    
    def get_users_by_server(self, server_id):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE server_id={};".format(server_id))
                users = cursor.fetchall()
                return users
        return None
        
    def get_user_in_server(self, user_id, server_id):
        with self.__connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM dbo.Users WHERE user_id={} AND server_id={};".format(user_id, server_id))
                user = cursor.fetchone()
                return user
        return None
        
    def add_member(self, server_id, user_id, username, ):
        conn = self.__connect()

if __name__ == '__main__':
    con = DbConn()
    #con.connect()
    con.add_server(861051867249639456, "Kyyysserver")
