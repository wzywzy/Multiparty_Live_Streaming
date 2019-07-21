import numpy as np
import random
import datetime
import math

RANDOM_SEED = 42
CHANGE_RATE = 30

class Sender:
    def __init__(self, id, bandwidth, bitrate, buffer_capacity):
        self.id = id
        self.bandwidth = bandwidth
        self.buffer_size = 0
        self.buffer_capacity = buffer_capacity
        self.frame_index = 0
        self.bandwidth_index = 0
        np.random.seed(RANDOM_SEED)
        self.bitrate = bitrate
        self.frame_amount = len(self.bandwidth)
        self.frame_size=[0]*self.frame_amount
        self.static_frame_size = [0]*self.frame_amount
        self.buffer_index = []
        self.frame_exist = False
    def frame_generate(self):
        if self.frame_exist == False:
            self.average_frame_size = abs(self.bitrate)
            self.frame_size[self.frame_index] = np.random.randint(self.average_frame_size/2,self.average_frame_size*1.5+1)  #simulate the codec errors
            self.static_frame_size[self.frame_index] = self.frame_size[self.frame_index]
            self.buffer_size = self.buffer_size + self.frame_size[self.frame_index]
            self.buffer_index.append(self.frame_index)
        self.frame_index = self.frame_index + 1
    def frame_set(self,frames):
        self.frame_exist = True
        self.frame_size.clear()
        self.static_frame_size.clear()
        self.frame_size.extend(frames)
        self.static_frame_size.extend(frames)
    def push_to_server(self):
        frame_pushed = []
        frame_pushed_size = []
        #IsAdequate = False
        while(len(self.buffer_index)>0):
            #print(len(self.bandwidth) )
            
            if(self.bandwidth[self.bandwidth_index] > self.frame_size[self.buffer_index[0]] ):
                self.bandwidth[self.bandwidth_index]= self.bandwidth[self.bandwidth_index]-self.frame_size[self.buffer_index[0]]
                self.buffer_size = self.buffer_size - self.frame_size[self.buffer_index[0]]
                frame_pushed_size.append(self.static_frame_size[self.buffer_index[0]])
                frame_pushed.append(self.buffer_index.pop(0))
                
                #IsAdequate = True
            else:
                if(len(self.buffer_index)!=0):
                    self.frame_size[self.buffer_index[0]] = self.frame_size[self.buffer_index[0]] - self.bandwidth[self.bandwidth_index]
                    #IsAdequate = False
                break
        self.bandwidth_index = self.bandwidth_index+1
        return frame_pushed , frame_pushed_size
    def set_Bitrate(self,bitrate):
        self.bitrate = bitrate

class Server:
    def __init__(self,sender_count,reciever_count):
        self.buffer = {}
        self.buffer_size ={}
        #self.IsComplete = {}
        for i in range(sender_count):
            self.buffer[i]={}
            self.buffer_size[i] = {}
            #self.IsComplete[i] = {}
            for j in range(reciever_count):
                self.buffer[i][j]=[]
                self.buffer_size[i][j] = []
                #self.IsComplete[i][j]=True
        #self.temp = 0
    def buffering(self,senderID,recieverID,index,frame_size):
            if len(index)!=0:
                self.buffer[senderID][recieverID].extend(index)
                self.buffer_size[senderID][recieverID].extend(frame_size)
            
class Reciever:
    def __init__(self, id, bitrate, QoeMetrix,sendercount, bandwidth, startup_delay):
        self.id = id
        self.bitrate = bitrate
        self.bandwidth = np.array(bandwidth)
        self.sendercount = sendercount
        self.startup_delay = startup_delay #for each sender,set a startup delay,for itself,set it to INF
        self.play_index = [0]*sendercount
        self.buffer_index = {}
        for sender in range(self.sendercount):
            self.buffer_index[sender]=[]
        self.buffer_size = 0
        self.rebuffer = [0]*self.sendercount
        self.time_index = -1
        self.QoeMetrix = QoeMetrix
        self.qoe = [0]*sendercount
        self.ready_to_play = []
        self.lastdelay = [0]*self.sendercount
        self.lastrebuffer = [0]*self.sendercount
        self.bitrate_history = []
        self.bitrate_history.append(bitrate)
        self.abandon_user= []
        self.schedule_stack = []
        self.bufferchange = [0]*self.sendercount
        for i in range(self.sendercount):
            if self.id != i:
                self.schedule_stack.append(i)
        for i in range(self.sendercount):
            if i!=self.id:
                self.ready_to_play.append(i)
        self.start_to_play = []
    def get_frame(self,server):
        self.time_index = self.time_index + 1
        while(self.bandwidth[self.time_index]>0):
            iterator = self.schedule_stack[0]
            if len(server.buffer_size[iterator][self.id])>0:
                if(server.buffer_size[iterator][self.id][0]<=self.bandwidth[self.time_index]):
                    self.buffer_index[iterator].append(server.buffer[iterator][self.id].pop(0))
                    self.bandwidth[self.time_index] = self.bandwidth[self.time_index] - server.buffer_size[iterator][self.id][0]
                    server.buffer_size[iterator][self.id].pop(0)
                    self.schedule_stack.pop(0)
                    self.schedule_stack.append(iterator)
                else:
                    server.buffer_size[iterator][self.id][0] = server.buffer_size[iterator][self.id][0] - self.bandwidth[self.time_index]
                    self.bandwidth[self.time_index] = 0
            else:
                self.schedule_stack.pop(0)
                self.abandon_user.append(iterator)
            if len(self.schedule_stack)==0:
                break
        self.schedule_stack.extend(self.abandon_user)
        self.abandon_user.clear()
    def play(self):
        for sender in range(self.sendercount):
            if len(self.buffer_index[sender])!=0:
                if len(self.buffer_index[sender])>1:
                    self.play_index[sender] = self.buffer_index[sender].pop(0)
                    self.play_index[sender] = self.buffer_index[sender].pop(0)
                else:
                    self.play_index[sender] = self.buffer_index[sender].pop(0)

            else:
                self.rebuffer[sender] = self.rebuffer[sender]+1
    def setBitrate(self,bitrate):
        self.bitrate_history.append(bitrate)
        self.bitrate = bitrate
    def Qoe(self):
        
        video_quality = [0]*self.sendercount
        jitter = [0]*self.sendercount
        rebuffer = [0]*self.sendercount
        delay = [0]*self.sendercount
        for i in range(self.sendercount):
            if (i!= self.id):
                video_quality[i] = self.bitrate[i]
                jitter[i] = abs(self.bitrate_history[-1][i]-self.bitrate[i])
                rebuffer[i] = self.rebuffer[i]
                delay[i] = self.time_index - self.play_index[i]
                temp = 6*self.QoeMetrix[i][0]*video_quality[i]-0.2*self.QoeMetrix[i][1]*jitter[i]-0.8*self.QoeMetrix[i][2]*(rebuffer[i]-self.lastrebuffer[i])-0.2*self.QoeMetrix[i][3]*(delay[i]-self.lastdelay[i])
                self.qoe[i]=temp
                self.bufferchange[i] = rebuffer[i]-self.lastrebuffer[i]
                #print(rebuffer[i]-self.lastrebuffer[i])
            else:
                self.qoe[i] = 0
        self.lastdelay = delay
        self.lastrebuffer = rebuffer
        return self.qoe    
    def getQoe(self,id,bitrate):  
        return bitrate
                    
        