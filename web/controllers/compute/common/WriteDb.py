import mysql.connector

class WriteDb():
    def __init__(self, sql):
        self.sql = sql

    def write(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Zx1993624!",
            database="stock_ai"
        )

        mycursor = mydb.cursor()
        mycursor.execute(self.sql)
        # result: [(tuple),] tuple list
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")


