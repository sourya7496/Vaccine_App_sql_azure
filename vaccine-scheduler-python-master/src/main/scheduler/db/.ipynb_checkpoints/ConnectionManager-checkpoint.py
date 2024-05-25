import pymssql
import os


class ConnectionManager:

    def __init__(self):
        self.server_name = os.getenv("Server") + ".database.windows.net"
        self.db_name = os.getenv("DBName")
        self.user = os.getenv("UserID")
        self.password = os.getenv("Password")
        self.conn = None
        

    def create_connection(self):
        try:
            ##self.conn = pymssql.connect(server=self.server_name, user=self.user, password=self.password, database=self.db_name, tds_version= "8.0", as_dict=True)
            self.conn = pymssql.connect(server="somondal.database.windows.net", user="somondal\@uw.edu", password="Fr@nce2006", database="hw3cse414", tds_version= "8.0")
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            print(db_err)
            quit()
        return self.conn

    def close_connection(self):
        try:
            self.conn.close()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            print(db_err)
            quit()
