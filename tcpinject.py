import socks
import socket
import threading

class conn_:
    def __init__(self,conn,handle_func,ignore_empty,socks5_proxy=None):
        self.conn = conn
        self.handle_func = handle_func
        self.ignore_empty = ignore_empty
        self.socks5_proxy = socks5_proxy

    def start(self,rport,rip):
        self.remote_conn = socks.socksocket()
        
        if self.socks5_proxy:
            pip,pport = self.socks5_proxy.split(':')#proxy ip & proxy port
            pport = int(pport)
            self.remote_conn.set_proxy(socks.PROXY_TYPE_SOCKS5,pip,pport)
            
        self.remote_conn.connect((rip,rport))
        
        threading.Thread(target=self.srclistener).start()
        threading.Thread(target=self.remotelistener).start()

        
    def srclistener(self):
        while True:
            data = self.conn.recv(10000000)
            if not data and self.ignore_empty:
                continue
            self.handle_func(packet(data,self.remote_conn,True,self))

    def remotelistener(self):
        while True:
            data = self.remote_conn.recv(10000000)
            if not data and self.ignore_empty:
                continue
            self.handle_func(packet(data,self.conn,False,self))


def start_deamon(srcip:str,rip:str,srcport:int,rport:int,listen:int,handle_func,ignore_empty=False,socks5_proxy=None):
    s = socks.socksocket()
    s.bind((srcip,srcport))
    if listen==-1:
        s.listen()
    else:
        s.listen(listen)
        
    while True:
        c,a = s.accept()
        conn = conn_(c,handle_func,ignore_empty,socks5_proxy)
        threading.Thread(target=conn.start,args=(rport,rip)).start()

def start_deamon_thread(srcip:str,rip:str,srcport:int,rport:int,listen:int,handle_func,ignore_empty=False,socks5_proxy=None):
    threading.Thread(target=start_deamon,args=(srcip,
                                               rip,
                                               srcport,
                                               rport,
                                               listen,
                                               handle_func,ignore_empty,socks5_proxy)).start()

class packet:
    def __init__(self,packet,conn,from_user:bool,conn_):
        self.conn = conn
        self.packet =  packet
        self.from_user = from_user
        self.conn_ = conn_

    def send(self):
        self.conn.send(self.packet)

    def get(self):
        return self.packet

    def set(self,data):
        self.packet = data
        
