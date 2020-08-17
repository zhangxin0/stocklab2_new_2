"""
 读取数据库最新时间
"""
import mysql.connector

class ReadCursor():

  def read(self):
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      passwd="Zx1993624!",
      database="stock_ai"
    )

    mycursor = mydb.cursor()
    sql_date = "select max(trade_date) from stock_info where symbol='000001.SZ';"
    # mycursor.execute("SELECT cursor_date FROM cursor_date")
    mycursor.execute(sql_date)
    # result: [(tuple),] tuple list
    myresult = mycursor.fetchall()
    return myresult[0][0]