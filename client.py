import socket
import  xml.etree.ElementTree as ET
import time
import threadpool
from multiprocessing.pool import ThreadPool  
from multiprocessing import Pool, cpu_count

tree = ET.parse('test.xml')
root = tree.getroot()
#indent(root)
a = ET.tostring(root, encoding='utf8', method='xml')
#root = ET.fromstring(a)

tree2 = ET.parse('test2.xml')
root2 = tree2.getroot()
#indent(root2)
a2 = ET.tostring(root2, encoding='utf8', method='xml')

tree3 = ET.parse('test3.xml')
root3 = tree3.getroot()
a3 = ET.tostring(root3, encoding='utf8', method='xml')

tree4 = ET.parse('test4.xml')
root4 = tree4.getroot()
a4 = ET.tostring(root4, encoding='utf8', method='xml')

arglist = [a, a2, a3, a4]

click = socket.socket()

env11 = 0

def work_thread(conn1):
    click.connect(('vcm-8948.vm.duke.edu', 12345))
    print("aaaaaaajhhjvhjfwekqr")
    click.send(conn1)
    time.sleep(1) 
    click.close()  

pool = threadpool.ThreadPool(4)
reqs = threadpool.makeRequests(work_thread, arglist)
[pool.putRequest(req) for req in reqs] 
pool.wait() 
print("over")