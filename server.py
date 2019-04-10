import psycopg2
from Task import Task

#def build_db():

conn = psycopg2.connect(database="exchange_db", user="postgres", password="psql")
print("Opened database successfully")
    
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS RECORD, TRANS_REQ, POSITIONS, ACCOUNT CASCADE;")
cur.execute('''CREATE TABLE ACCOUNT
           (ACCOUNT_ID INT PRIMARY KEY NOT NULL,
           BALANCE  INT    NOT NULL);''')
cur.execute('''CREATE TABLE POSITIONS
               (POS_ID SERIAL PRIMARY KEY NOT NULL,
               ACCOUNT_ID INT  REFERENCES ACCOUNT(ACCOUNT_ID),
               SYM  TEXT NOT NULL,
               NUMS INT  NOT NULL,
               UNIQUE(ACCOUNT_ID,SYM));''')
cur.execute('''CREATE TABLE TRANS_REQ
                   (TRANS_ID SERIAL PRIMARY KEY NOT NULL,
                   ACCOUNT_ID INT REFERENCES ACCOUNT(ACCOUNT_ID),
                   SYM  TEXT NOT NULL,
                   LIMIT_PRICE FLOAT NOT NULL,
                   LEFT_NUMS INT  NOT NULL);''')
cur.execute('''CREATE TABLE RECORD
                   (RECORD_ID SERIAL PRIMARY KEY NOT NULL,
                   TRANS_ID INT NOT NULL,
                   TIME INT NOT NULL,
                   ACT_PRICE FlOAT NOT NULL,
                   SHARE_NUMS INT  NOT NULL);''')
print("Table created successfully")
conn.commit()
conn.close()

import socket
from multiprocessing.pool import ThreadPool  
from multiprocessing import Pool, cpu_count
#print(cpu_count())

server = socket.socket()
server.bind(('0.0.0.0', 12345))
server.listen(5)
            
def work_thread(conn1):
    while True:
        data = conn1.recv(2048)
        if data:
            try:
                #print(data.decode('utf8'))
                new_task = Task()
                mess = new_task.execute1(data.decode('utf8'))     
                #print(str(mess))     
                conn1.sendall(str(mess).encode())    
            except Exception as e:     
                print("error",e)   
        else:
            conn1.close()
            break
def thread_handle():
    t_pool = ThreadPool(8)  
    while True:
        conn1,addr = server.accept()
        t_pool.apply_async(work_thread, args=(conn1,))  
thread_handle()
conn.close()
