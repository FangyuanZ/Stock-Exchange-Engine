import cProfile
import socket
import  xml.etree.ElementTree as ET
import time
import  xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree
import random

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

res_root = Element('create')
generate_account_number = 5
dict_account_balance = {}

id_random = random.randint(1, generate_account_number + 1)
balance = random.randint(200000, 500000) 
dd = {'balance': str(balance), 'id': str(id_random)}
ET.SubElement(res_root, 'account', dd)

# generate random symbol
s = ["ABC", "SYM", "HAHA", "XIXI"]

for i in range(5):
    num = random.randint(0, len(s) - 1)
    sub_root = ET.SubElement(res_root, 'symbol', {'sym': s[num]})
    temp = ET.SubElement(sub_root, 'account', {'id': str(id_random)})
    share_num = random.randint(100, 500)
    temp.text = str(share_num)
    
indent(res_root)    
result = ET.tostring(res_root, encoding='utf8', method='xml').decode('utf8')
leng = str(result)
len1 = str(len(leng))
leng = len1+'\n'+leng

click = socket.socket()
click.connect(('vcm-8948.vm.duke.edu', 12345))

click.send(leng.encode('utf8'))
data1 = click.recv(20480)
#print(data1.decode('utf8'))


#trans_id = random.randint(1, generate_account_number + 1)
trans_root = Element('transactions', {'id': str(id_random)})

order_num = 10
cancel_num = 3
query_num = 2

for i in range(order_num):
    ran_sym = random.randint(0, len(s) - 1)
    amount = random.randint(-300, 300)
    limit = random.uniform(100.00, 200.00)
    limit = round(limit, 2)
    ET.SubElement(trans_root, 'order', {'Asym': s[ran_sym], 'amount': str(amount), 'limit': str(limit)})
for i in range(query_num):
    transaction_id = random.randint(1, order_num)
    ET.SubElement(trans_root, 'query', {'id': str(2*transaction_id)})
        
for i in range(cancel_num):
    transaction_id = random.randint(1, order_num/2)
    ET.SubElement(trans_root, 'cancel', {'id': str(2*transaction_id)})    
    
indent(trans_root)    
result1 = ET.tostring(trans_root, encoding='utf8', method='xml').decode('utf8')
result1 = result1.replace('Asym', 'sym')
leng1 = str(result1)
len11 = str(len(leng1))
leng1 = len11+'\n'+leng1
click.send(leng1.encode('utf8'))
data2 = click.recv(20480)
#print(data2.decode('utf8'))

click.close()
