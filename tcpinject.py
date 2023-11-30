import socks
import socket
import threading
import ssl

class conn_:
    def __init__(self,conn,handle_func,ignore_empty,srcip,srcport,socks5_proxy=None,thread_data=None):
        self.conn = conn
        self.handle_func = handle_func
        self.ignore_empty = ignore_empty
        self.socks5_proxy = socks5_proxy
        self.srcip = srcip
        self.srcport = srcport
        self.thread_data = thread_data

    def start(self,rport,rip,use_ssl):
        self.remote_conn = socks.socksocket()
        
        if self.socks5_proxy:
            pip,pport = self.socks5_proxy.split(':')#proxy ip & proxy port
            pport = int(pport)
            self.remote_conn.set_proxy(socks.PROXY_TYPE_SOCKS5,pip,pport)

        if use_ssl:
            #print(rip,rport)
            context = ssl.create_default_context()
            self.remote_conn = context.wrap_socket(self.remote_conn, server_hostname=rip)
        self.remote_conn.connect((rip,rport))
        
        self.remote_ip = rip
        self.remote_port = rport
        
        threading.Thread(target=self.srclistener).start()
        threading.Thread(target=self.remotelistener).start()

        
    def srclistener(self):
        while True:
            try:
                data = self.conn.recv(10000000)
                if not data and self.ignore_empty:
                    continue
                self.handle_func(packet(data,self.remote_conn,True,self))
            except ConnectionError:
                #self.conn.close()
                break

    def remotelistener(self):
        while True:
            try:
                data = self.remote_conn.recv(10000000)
                if not data and self.ignore_empty:
                    continue
                self.handle_func(packet(data,self.conn,False,self))
            except ConnectionError:
                #self.conn.close()
                break


def start_deamon(srcip:str,rip:str,srcport:int,rport:int,listen:int,handle_func,ignore_empty=False,socks5_proxy=None,use_ssl=False,cert_pair=None,thread_data:str=None):

    #srcip is your ip
    #rip is remote ip of server
    #srcport is your port, where client should be connected
    #rport if remote port
    #listen is a number of connections, which should work with your device
    #if listen = -1, it is infinitive
    #handle_func is a function, which will handle packets
    #ignore_empty is a bool parametr,which ignores empty packets if it is False
    #socks5_proxy is an ip and port of proxy, which you wanna connect from
    #use_ssl is a bool parametr,which tells program to connect server using ssl
    #cert_pair is a tuple of pathes to a keyfile and certfile

    s = socks.socksocket()
    if cert_pair:
        s = ssl.wrap_socket(s, server_side=True, keyfile=cert_pair[0], certfile=cert_pair[1])
        
    s.bind((srcip,srcport))
    if listen==-1:
        s.listen()
    else:
        s.listen(listen)
        
    while True:
        try:
            c,a = s.accept()
            conn = conn_(c,handle_func,ignore_empty,srcip,srcport,socks5_proxy,thread_data)
            threading.Thread(target=conn.start,args=(rport,rip,use_ssl)).start()
        except (ConnectionError,ssl.SSLError) as e:
            print('Error',e)


def start_deamon_thread(srcip:str,rip:str,srcport:int,rport:int,listen:int,handle_func,ignore_empty=False,socks5_proxy=None,use_ssl=False,cert_pair=None,thread_data:str=None):
    threading.Thread(target=start_deamon,args=(srcip,
                                               rip,
                                               srcport,
                                               rport,
                                               listen,
                                               handle_func,ignore_empty,socks5_proxy,
                                               use_ssl,
                                               cert_pair,
                                               thread_data)).start()

class packet:
    def __init__(self,packet,conn,from_user:bool,conn_):
        self.conn = conn
        self.packet =  packet
        self.from_user = from_user
        self.connobj = conn_

    def send(self):
        self.conn.send(self.packet)

    def get(self):
        return self.packet

    def set(self,data):
        self.packet = data

    def replace(self,str0,str1):
        self.packet = self.packet.replace(str0,str1)
        
