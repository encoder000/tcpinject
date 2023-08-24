import tcpinject
import time
import random
import threading


class prog:

    def __init__(self):
        self.packets = []
        
    def catcher(self,packet):
        self.packets.append(packet)
        
if __name__ == '__main__':
    ftool = prog()
    tcpinject.start_deamon_thread('127.0.0.1',
                                  '185.117.155.43',
                                  80,
                                  80,
                                  -1,
                                  ftool.catcher,
                                  ignore_empty=True)

    while True:
        #print('e')
        for i in ftool.packets:
            data = i.get()
            if data:
                try:
                    print(data)
                    to_snd = input('Send: ')
                    if to_snd:
                        i.set(eval(to_snd))
                    i.send()
                    
                except ConnectionError:
                    print('Connection is dead XD')
            del ftool.packets[0]
            #print(len(ftool.packets))
