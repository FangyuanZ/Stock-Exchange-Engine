from XML_parse import XML_parse
import  xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree
from Exchange import Exchange
import psycopg2
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def check_buyvalid(cur, acc_id, symbol, limit, amount):
    str1 = "SELECT BALANCE FROM ACCOUNT WHERE ACCOUNT_ID = " + acc_id + ";"
    cur.execute(str1)  
    balance1 = cur.fetchone()    
    balance = balance1[0] 
    limit = float(limit)
    amount=int(amount)
    total_cost = limit*amount
    if balance >= total_cost:
        str4 = "SELECT BALANCE FROM ACCOUNT WHERE ACCOUNT_ID = " + acc_id + " FOR UPDATE;"
        cur.execute(str4)
        balance1 = cur.fetchone()
        balance = balance1[0]
        balance-= total_cost
        ssss = str(balance)
        str5 = "UPDATE ACCOUNT set BALANCE = " + str(balance) + " WHERE ACCOUNT_ID = " + acc_id + ";"
        cur.execute(str5)
        return "True"
    else:
        # error = ET.SubElement(response_root, 'error')
        # error.text = "Insufficient Balance To Purchase"
        str55 = "Insufficient Balance To Purchase"
        return str55

def check_sellvalid(cur, acc_id, symbol, limit, amount):  
    str222 = "SELECT NUMS FROM POSITIONS WHERE ACCOUNT_ID = " + acc_id + " AND SYM = '" + symbol + "' FOR UPDATE;"
    amount = -amount
    cur.execute(str222)
    num = cur.fetchone()
    if not num:
      # error = ET.SubElement(response_root, 'error')
      # error.text = "Trying to Sell Non-exist Stock"
      str55 = "Trying to Sell Non-exist Stock"
      return str55
    nums = num[0]
    if nums >= amount:
        return "True"
    else:
        # error = ET.SubElement(response_root, 'error')
        # error.text = "Insufficient Number of Stocks to Sell"
        return "Insufficient Number of Stocks to Sell"
        
class account:
    id = 0
    balance = 0
    # map key = symbol, value = number of shares 
    position = {} 
    
class Task:
    def __init__(self):
        pass
    def execute1(self, info):
        try:
            conn = psycopg2.connect(database="exchange_db", user="postgres", password="psql")
            #print("Opened database successfully")
            cur= conn.cursor()
            info = info.lstrip('1234567890\n')
        except Exception as e:
            print('Can not open database:',e)
        xml = XML_parse(info,cur)
        root = ET.fromstring(info)
        response_root = Element('results')
        if root.tag == 'create':
                #Extract account info from xml file with a create tag
            for child in root:
                if child.tag == 'account':
                    acc_id = child.get('id')
                    acc_balance = child.get('balance')
                    try:
                        xml.handle_account(cur, acc_id, acc_balance, response_root)
                        conn.commit()
                    except Exception as e:
                        print("Handle account failure")
                    #Generate XML response
                    #                    ET.SubElement(response_root, 'created', {'id': acc_id})
                    
                if child.tag == 'symbol':
                    symbol = child.get('sym')
                    for elem in child.iter(tag='symbol'):
                        acc_id = elem.find('account').get('id')
                        num_of_share = elem.find('account').text
                        try:
                            valid2 = xml.handle_position(cur, acc_id, symbol, num_of_share, response_root)
                            conn.commit()
                        except Exception as e:
                            print("Handle positions failure")
                            #Generate XML response
                        if valid2:
                            dd = dict(Asym=symbol, id=acc_id)
                            ET.SubElement(response_root, 'created', dd)
                                    
        if root.tag == 'transactions':            
            acc_id = root.get('id')  
            #check account_id valid
            try:
                str666 = "SELECT ACCOUNT_ID FROM ACCOUNT WHERE ACCOUNT_ID = " + str(acc_id) + " FOR UPDATE;"
                cur.execute(str666);
                rows = cur.fetchall()
            except Exception as e:
                print("Fail to access ACCOUNT table", e)
            if len(rows)==0 :
                error = ET.SubElement(response_root, 'error')
                error.text = "Invalid Account for Transactions"
                try:
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print("fail to commit and close database",e)
                indent(response_root)         
                result11 = ET.tostring(response_root, encoding='utf8', method='xml').decode('utf8')
                return result11
            for child in root:
                acc_id = root.get('id')
                if child.tag == 'order':
                    symbol = child.get('sym')
                    amount = child.get('amount')
                    limit = child.get('limit')
                    amount = int(amount)
                    if amount >= 0:
                        try:
                            valid = check_buyvalid(cur, acc_id, symbol, limit, amount)
                            conn.commit()
                        except Exception as e:
                            print("check buyvalid error",e)
                    if amount < 0:
                        try:
                            valid = check_sellvalid(cur, acc_id, symbol, limit, amount)
                            conn.commit()
                        except Exception as e:
                            print("check sellvalid error",e)

                    if valid != "True": #handle all errors in order 
                    #response error
                        dict_order = {'Asym': symbol, 'Bamount': str(amount), 'Climit': limit}
                        error = ET.SubElement(response_root, 'error', dict_order)  
                        error.text = valid
                        continue
                    acc_id = int(acc_id)
                    try:
                        return_tran_id = xml.handle_transaction(cur, acc_id, symbol, limit, amount)
                        conn.commit()
                    except Exception as e:
                        print("handle transaction error",e)
                    deal = Exchange(cur) 
                    try:
                        deal.do_exchange(return_tran_id)
                        conn.commit()
                    except Exception as e:
                        print("do exchange stocks error",e)
                    dict_order = {'Asym': symbol, 'Bamount': str(amount), 'Climit': limit, 'id': str(return_tran_id)}
                    ET.SubElement(response_root, 'opened', dict_order)   

                if child.tag == 'cancel':
                    transaction_id = child.get('id')
                    try:
                        xml.handle_cancel(cur, transaction_id, response_root, acc_id)
                        conn.commit()
                    except Exception as e:
                        print("cancel error",e)
                if child.tag == 'query':
                    transaction_id = child.get('id')
                    try:
                        xml.check_status(cur, transaction_id, response_root, acc_id)
                    except Exception as e:
                        print("check status error",e)
                    #Generate XML response                    
        try:
            conn.close()
        except Exception as e:
            print("cannot close connection to the database")
        indent(response_root)         
        result = ET.tostring(response_root, encoding='utf8', method='xml').decode('utf8')
        result = result.replace('Asym', 'sym').replace('Bamount', 'amount').replace('Climit', 'limit').replace('Ashares', 'shares')
        return result
        #print(str(result))
            
                        




