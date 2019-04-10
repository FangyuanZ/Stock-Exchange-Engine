import psycopg2

import  xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
import time

class XML_parse:
    def __init__(self, info,cur):
      self.data = info
      self.cur = cur
    
    def handle_account(self, cur, id1, balance, response_root):
      strr = "SELECT ACCOUNT_ID FROM ACCOUNT WHERE ACCOUNT_ID = " + str(id1) + " FOR UPDATE;"
      cur.execute(strr);
      rows = cur.fetchall()
      if rows:
        # the account already existed
        error = ET.SubElement(response_root, 'error', {'id': id1})
        error.text = "Account number already exists"
        return
      str1 = "INSERT INTO ACCOUNT(ACCOUNT_ID, BALANCE) VALUES(" + str(id1) + "," + str(balance) +");"      
      cur.execute(str1)
      ET.SubElement(response_root, 'created', {'id': id1})
     
#      print(str1)
#    def handle_position()
    def handle_position(self, cur, acc_id, sym, nums, response_root):
      str666 = "SELECT ACCOUNT_ID FROM ACCOUNT WHERE ACCOUNT_ID = " + str(acc_id) + " FOR UPDATE;"
      cur.execute(str666);
      rows = cur.fetchall()
      if len(rows) == 0:
          error = ET.SubElement(response_root, 'error', {'id': acc_id})
          error.text = "Invalid Account to Add Positions"
          return False
      str2 = "INSERT INTO POSITIONS(ACCOUNT_ID, SYM, NUMS) VALUES(" + str(acc_id) +",'" + str(sym) + "'," + str(nums) + ") ON CONFLICT(ACCOUNT_ID, SYM) DO UPDATE SET NUMS=POSITIONS.NUMS+" + nums +" WHERE POSITIONS.ACCOUNT_ID=" + str(acc_id) + " AND POSITIONS.SYM=" + "'" + str(sym) + "'" + " ;"
#      print(str2)
      cur.execute(str2)
      return True
    def handle_transaction(self, cur, acc_id, sym, limit, nums):
    #check error?
      str3 = "INSERT INTO TRANS_REQ(ACCOUNT_ID, SYM, LIMIT_PRICE, LEFT_NUMS) VALUES(" + str(acc_id) +",'" + str(sym) + "'," + str(limit) + ","  + str(nums) + ") RETURNING TRANS_ID;"
      cur.execute(str3)
      testt = cur.fetchone()
      return testt[0]
      #match
    # def handle_record(self, cur, trans_id, time, price, nums):
    #   rec_time = time.time()
    #   print("TIME: ", rec_time)

    #   str4 = "INSERT INTO RECORD(TRANS_ID, TIME, ACT_PRICE, SHARE_NUMS) VALUES(" + str(trans_id) +"," + str(rec_time) + "," + str(price) + str(nums) + ");"
    #   cur.execute(str4)  
    #   print(str4)
      
    def check_status(self, cur, trans_id, response_root, acc_id):      
      str5 = "SELECT LEFT_NUMS FROM TRANS_REQ WHERE TRANS_ID = " + str(trans_id) + ";"
      cur.execute(str5)
      left_num = cur.fetchall()
      str6 = "SELECT TIME, ACT_PRICE, SHARE_NUMS FROM RECORD WHERE TRANS_ID = " + str(trans_id) + ";"
      cur.execute(str6)
      check_st = cur.fetchall()
      if len(left_num) == 0 and len(check_st) == 0:
          error = ET.SubElement(response_root, 'error', {'id': trans_id})  
          error.text = "Invalid Transaction ID to Query"  
          return
      else:
          new_root = ET.SubElement(response_root, 'status', {'id': trans_id})         
      if left_num:
          for num in left_num:
              ET.SubElement(new_root, 'open', {'shares': str(num[0])})            
      for check in check_st:
          if check[1] == -1:
                      #cancel
              dict_order = {'shares': str(check[2]), 'time': str(check[0])}
              ET.SubElement(new_root, 'canceled', dict_order)                      
          else:
                      #execute
              dict_order = {'shares': str(check[2]), 'price': str(check[1]), 'time': str(check[0])}
              ET.SubElement(new_root, 'executed', dict_order)
      

    def handle_cancel(self, cur, trans_id, response_root, acc_id):
        #check if transid exist                                                                                                              
        str7 = "SELECT LEFT_NUMS, LIMIT_PRICE, ACCOUNT_ID FROM TRANS_REQ WHERE TRANS_ID = " + str(trans_id) + " AND ACCOUNT_ID = " +str(acc_id) + " FOR UPDATE;"
        cur.execute(str7)
        check_trans = cur.fetchall()
        if check_trans:
            new_root = ET.SubElement(response_root, 'canceled', {'id': trans_id})
            time1 = int(time.time()) #time?????                                                                                                                  
            dict_order = {'shares': str(check_trans[0][0]), 'time': str(time1)}
            ET.SubElement(new_root, 'canceled', dict_order)
            strr = "SELECT SHARE_NUMS, ACT_PRICE, TIME FROM RECORD WHERE TRANS_ID = " + str(trans_id) + " FOR UPDATE;"
            cur.execute(strr)
            check_st = cur.fetchall()
            for check in check_st:
              dict1 = {'Ashares': str(check[0]), 'price': str(check[1]), 'time': str(check[2])}
              ET.SubElement(new_root, 'executed', dict1)
            str8 = "DELETE FROM TRANS_REQ WHERE TRANS_ID = " + trans_id + ";"
            cur.execute(str8)
            nummm = int(check_trans[0][0])
            if nummm > 0:
                str4 = "SELECT BALANCE FROM ACCOUNT WHERE ACCOUNT_ID = " + str(check_trans[0][2]) + " FOR UPDATE;"
                cur.execute(str4)
                balance1 = cur.fetchone()
                balance = balance1[0]
                price1 = float(check_trans[0][1])
                balance += price1*nummm
                str5 = "UPDATE ACCOUNT set BALANCE = "+str(balance)+" WHERE ACCOUNT_ID = " + str(check_trans[0][2]) + ";"
                cur.execute(str5)
            str4 = "INSERT INTO RECORD(TRANS_ID, TIME, ACT_PRICE, SHARE_NUMS) VALUES(" + str(trans_id) +"," + str(time1) + "," + str(-1) + "," + str(check_trans[0][0]) + ");"
            cur.execute(str4)
        else:
            error = ET.SubElement(response_root, 'error', {'id': trans_id})
            error.text = "Invalid Transaction ID to Cancel"
        return response_root


        
       
