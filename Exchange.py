import psycopg2
import time

def check_selllist(cur):
        str1 = "SELECT * FROM TRANS_REQ WHERE LEFT_NUMS < 0;"
        cur.execute(str1)
        selllist = cur.fetchall()
        return selllist
def check_buylist(cur):
        str1 = "SELECT * FROM TRANS_REQ WHERE LEFT_NUMS > 0;"
        cur.execute(str1)
        buylist = cur.fetchall()
        return buylist
    
def remove_stock(cur, trade_num, trans_id):
        #change transactions left nums
        str3 = "SELECT LEFT_NUMS FROM TRANS_REQ WHERE TRANS_ID= " + str(trans_id) + ";"
        cur.execute(str3)
        num = cur.fetchone()
        nums = num[0]
        if nums > 0:  #buy side
            nums-=trade_num
        else:    #sell side
            nums += trade_num
        str66= "UPDATE TRANS_REQ SET LEFT_NUMS = "+str(nums)+" WHERE TRANS_ID = "+str(trans_id) + ";"     
        cur.execute(str66)
        if nums == 0:
            str4 = "DELETE FROM TRANS_REQ WHERE TRANS_ID = " + str(trans_id) + ";"            
            cur.execute(str4)
        return
            #delete
def buy_item(cur, trade_num, account_id, limit_price, sym, trans_id):
        #change account balance if sell
        if trade_num < 0:
            str4 = "SELECT BALANCE FROM ACCOUNT WHERE ACCOUNT_ID = " + str(account_id) + " FOR UPDATE;"
            cur.execute(str4)
            balance1 = cur.fetchone()
            balance = balance1[0]
            balance-= trade_num * limit_price
            str5 = "UPDATE ACCOUNT set BALANCE = "+str(balance)+" WHERE ACCOUNT_ID = " + str(account_id) + ";"
            cur.execute(str5)
        #change positions nums
        str6 = "SELECT NUMS FROM POSITIONS WHERE SYM = '" + str(sym) + "' FOR UPDATE;"
        cur.execute(str6)
        stock_nums1 = cur.fetchone()
        stock_nums = stock_nums1[0]
        stock_nums+=trade_num
        str7 = "UPDATE POSITIONS set NUMS = "+str(stock_nums)+" WHERE SYM = '" + sym + "' AND ACCOUNT_ID = " + str(account_id) + ";"
        cur.execute(str7)
        #add record
        time1 = int(time.time())
        str8 = "INSERT INTO RECORD(TRANS_ID, TIME, ACT_PRICE, SHARE_NUMS) VALUES(" + str(trans_id) +"," + str(time1) + "," + str(limit_price) + "," + str(trade_num) + ");"
        cur.execute(str8)
        
class Exchange:
    def __init__(self,cur):
        self.cur = cur

    def do_exchange(self, trans_id):
        str2 = "SELECT * FROM TRANS_REQ WHERE TRANS_ID = " + str(trans_id) + " FOR UPDATE;"
        self.cur.execute(str2)
        trans_info = self.cur.fetchone()
        #buy
        if trans_info[4] > 0: #buy
            check_list = check_selllist(self.cur)
            summ = trans_info[4]
            for item in check_list:
                if summ<=0:
                    break
                if item[3]<=trans_info[3] and item[2]==trans_info[2] and item[1]!= trans_info[1]:
                    trade_num = min(trans_info[4],-1*item[4])
                    remove_stock(self.cur, trade_num, trans_id)
                    remove_stock(self.cur, trade_num, item[0])
                    summ -= trade_num
                    buy_item(self.cur, trade_num, trans_info[1], item[3], item[2], trans_id)  #buy
                    buy_item(self.cur, -1*trade_num, item[1], item[3], item[2], item[0])       #sell
        
        if trans_info[4] < 0:  #sell
            check_list = check_buylist(self.cur)
            summ = -trans_info[4]
            for item in check_list:
                if summ<=0:
                    break
                if item[3]>=trans_info[3] and item[2]==trans_info[2] and item[1]!= trans_info[1]:
                    trade_num = min(-trans_info[4],item[4])
                    remove_stock(self.cur, trade_num, trans_id)
                    remove_stock(self.cur, trade_num, item[0])
                    summ -= trade_num
                    buy_item(self.cur, -trade_num, trans_info[1], trans_info[3], item[2], trans_id)  #sell
                    buy_item(self.cur, trade_num, item[1], trans_info[3], item[2], item[0])       #buy
