import threading
import time
import socket
import  xml.etree.ElementTree as ET
import time
 
class ThreadImpl(threading.Thread):# inherit from threading.Thread
    def __init__(self):
        threading.Thread.__init__(self)
 
    # rewrite run method
    def run(self, arglist):
        self.test(arglist)
 
    # code for testing
    def test(self, arglist):
        print ("test"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
 
if __name__ == '__main__':
    # number of thread    
    tree = ET.parse('test.xml')
    root = tree.getroot()
    #indent(root)
    a = ET.tostring(root, encoding='utf8', method='xml')
    #root = ET.fromstring(a)

    tree2 = ET.parse('test2.xml')
    root2 = tree2.getroot()
    #  indent(root2)
    a2 = ET.tostring(root2, encoding='utf8', method='xml')

    tree3 = ET.parse('test3.xml')
    root3 = tree3.getroot()
    a3 = ET.tostring(root3, encoding='utf8', method='xml')
    tree4 = ET.parse('test4.xml')
    root4 = tree4.getroot()
    a4 = ET.tostring(root4, encoding='utf8', method='xml')
    thread_count = 100
    
    # thread list
    threads = []
    for i in range(4):
        # create new thread
        t = ThreadImpl()
        
        # start a new thread
        t.start(arglist)
        
        # add thread to thread list
        threads.append(t)
        
    for t in threads:
        # waiting for threads to finish
        t.join()
        
    print ('end:'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
