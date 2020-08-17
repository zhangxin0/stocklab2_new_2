import mysql.connector

class ReadDb():
    def __init__(self, sql):
        self.sql = sql

    def read(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Zx1993624!",
            database="stock_ai"
        )

        mycursor = mydb.cursor()
        mycursor.execute(self.sql)
        # result: [(tuple),] tuple list
        myresult = mycursor.fetchall()
        return myresult


