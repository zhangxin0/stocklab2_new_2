from web.controllers.compute.common.ReadDb import ReadDb
import mysql.connector

# 产生所有股票的有效列表
class Gen_Stock_List():
    def gen_stock_list(self):
        sql = 'Select distinct symbol from stock_info'
        read = ReadDb(sql)
        res = read.read()
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Zx1993624!",
            database="stock_ai"
        )
        mycursor = mydb.cursor()
        for e in res:
            sql = f"Insert into stock_list(symbol) values ('{e[0]}')"
            mycursor.execute(sql)
        mydb.commit()

gen = Gen_Stock_List()
gen.gen_stock_list()