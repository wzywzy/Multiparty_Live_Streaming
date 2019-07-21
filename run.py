import env
import algrithm
import numpy as np
import cluster 
import os
import csv
import time as tm
#cooked data
#rf = open('data_fixed.txt', 'w') 
#writerQoe = writer(mf)
#qf = open('data_Single','w')
#bf = open('data_NLP.txt','w')
#jf = open('data_FBA.txt','w')
df = open('canshutaolun1.txt','w')
#bfr = open('bufferD.txt','w')
#tc = open('clustertime.txt','w')
#tl = open('lptime.txt','w')
#tf = open('fbtime.txt','w')
#ts = open('sumtime.txt','a')
#t1 = open('br1.txt','w')不同设置对应不同码率
#t2 = open('br2.txt','w')
#init each bandwidth
FILE_PATH = './downlink_trace/'
LP_GAP = 1000
FB_GAP = 200
usercount = 5
files = os.listdir(FILE_PATH)
QoeMetrix = np.ones((5,5,4), dtype=np.int16)
QoeMetrix[0][2][0] = 0.6
QoeMetrix[0][2][2] = 1.4
QoeMetrix[1][3][0] = 1.2
QoeMetrix[1][3][2] = 0.8
#for adjust in range(50):
k=0

for k1 in range(40):
    k =k +0.1
    j1=0
    for k2 in range(40):
        j1 = j1+0.1
        bitrate_list =[0]*usercount
        AvgThpDown = np.random.randint(2000/30,3000/30,usercount) #generate average downlink throughput 
        AvgThpUp = np.random.randint(500/30,1000/30,usercount) #generatre average uplink throughput
        downlink_trace = {}
        real_trace = []
        for file in files:
            with open(FILE_PATH+file, 'r') as f:
                bandwidth = []
                for line in f:
                    if line[0]!='p':
                        bandwidth.extend([int(line)]*15)
                real_trace.append(bandwidth)
        downlink_trace[0] = real_trace[0][0:40000]
        downlink_trace[1] = real_trace[0][40000:80000]
        downlink_trace[2] = real_trace[1][0:30000]
        downlink_trace[3] = real_trace[1][30000:60000]
        downlink_trace[4] = real_trace[2][0:40000]
        #print(downlink_trace[1])
        uplink_trace = {}
        for count in range(5):
            #uplink_trace[count]  =abs(np.random.poisson(AvgThpUp[count],20000))
            uplink_trace[count]  =np.array([1500]*20000)
            #print(uplink_trace[count])

        #set up senders server and recievers
        Senders = []
        for  count in range(len(AvgThpDown)):
            Senders.append(env.Sender(count, uplink_trace[count],AvgThpUp[count], 0))
        Server = env.Server(usercount,usercount)
        #print(Server.IsComplete)
        Recievers = []
        for count in range(len(AvgThpDown)):
            Recievers.append(env.Reciever(count,bitrate_list,QoeMetrix,usercount,downlink_trace[count],10))
        #estimate the bandwidth
        init_estimate = []
        for i in range(usercount):
            trace_to_estimate = downlink_trace[i][1000:5000]
            
            init_estimate.append(algrithm.estimate(trace_to_estimate))
        init_estimate_1 = []
        for i in range(usercount):
            trace_to_estimate = uplink_trace[i][0:50].tolist()
        # print(trace_to_estimate)
            init_estimate_1.append(algrithm.estimate(trace_to_estimate))
        #linear plan for the first time
        result = {}
        time_start = tm.time_ns()
        #print(init_estimate)
        result =algrithm.offline_solve(usercount,init_estimate,init_estimate,init_estimate_1,QoeMetrix,Recievers)
        time_end = tm.time_ns()
        time_last = time_end-time_start
        #tl.write(str(time_last)+'\n')
        last_est = init_estimate
        #init data to be pass
        init_bitrate_sender = [0]*usercount
        init_bitrate_reciever  = [[0] * usercount for row in range(usercount)]
        #cluster for the first time
        for i in range(usercount):
            time_start = tm.time_ns()
            output,low,high=cluster.kMeans(i,result[i],Recievers)
            time_end = tm.time_ns()
            time_last = time_end-time_start
            #tc.write(str(time_last)+'\n')
            for j in range(usercount):
                init_bitrate_reciever[j][i]=output[j]
            init_bitrate_sender[i]=low/3+high
        #print(init_bitrate_reciever) 
        #print(init_bitrate_sender)
        for reciever in Recievers:
            reciever.setBitrate(init_bitrate_reciever[reciever.id])
        for sender in Senders:
            sender.set_Bitrate(init_bitrate_sender[sender.id])

        #begin to run in 10000 frames, init some parameters which are needed
        lastbuffer = [[0]*usercount for row in range(usercount)]
        lastrebuffer = [[0]*usercount for row in range(usercount)]
        average_bitrate_last = [0]*usercount
        error_sum = [[0]*usercount for row in range(usercount)]
        qoe_queue=[]
        Sumq = 0
        time_lp = 0
        time_fba = 0
        time_cluster = 0
        delay = 0
        bbitrate = 0
        rrebuffer = 0
        jjitter = 0
        qqqoe = 0
        for time in range(20000):
            for sender in Senders:
                sender.frame_generate()
                data1,data2 = sender.push_to_server()
                
                #print(len(data))
                for reciever in Recievers:
                    dataUsed1 = data1
                    dataUsed2 = data2
                    if sender.id != reciever.id:
                        Server.buffering(sender.id , reciever.id,dataUsed1,dataUsed2)
            for reciever in Recievers:
                reciever.get_frame(Server)
                reciever.play()
            if(time%100 == 1):
            #if(time%100 == adjust):#this part is for output result
                average_rebuffer = [0]*usercount
                
                for reciever in Recievers:
                    average_bitrate = sum(bitrate for bitrate in reciever.bitrate)/(usercount-1)
                    #print(average_bitrate)
                    jitter =abs( average_bitrate - average_bitrate_last[reciever.id])
                    #print(jitter)
                    #jf.write(str(jitter)+'\n')
                    average_bitrate_last[reciever.id] = average_bitrate
                    average_rebuffer =sum(rebuffer for rebuffer in reciever.bufferchange)/(usercount-1)
                    average_delay = sum(delay for delay in reciever.lastdelay)
                    #rf.write(str(average_rebuffer)+'\n')
                    reciever.Qoe()
                    average_qoe = sum(qoe for qoe in reciever.qoe)/(usercount-1)
                    qoe_queue.append(average_qoe[1])
                #br1 = Recievers[0].bitrate[2]
                #t1.write(str(br1)+'\n')
                #br2 = Recievers[1].bitrate[3]
                #t2.write(str(br2)+'\n')
                #bf.write(str(average_bitrate)+'\n')
                #qf.write(str(average_qoe[1])+'\n')
                #print(Recievers[3].bitrate[2])
                #bfr.write(str(len(Recievers[4].buffer_index[2]))+'\n')
                #print(len(Recievers[0].buffer_index[2]))
                # if reciever.id == 3:
                        #print(average_delay)
                    delay = delay + average_delay 
                    bbitrate =  bbitrate +average_bitrate
                    rrebuffer = rrebuffer+average_rebuffer 
                    jjitter = jjitter + jitter
            #if(time%(LP_GAP)==LP_GAP-adjust*15):
            if(time%(LP_GAP)==LP_GAP-1):
                estimate = []
                for i in range(usercount):
                    trace_to_estimate = downlink_trace[i][time-50:time]
                    estimate.append(algrithm.estimate(trace_to_estimate))
                estimate_1 = []
                for i in range(usercount):
                    trace_to_estimate = uplink_trace[i][time:time+50].tolist()
                    estimate_1.append(algrithm.estimate(trace_to_estimate))
                #linear plan
                time_start = tm.time_ns()
                result =algrithm.offline_solve(usercount,estimate,last_est,estimate_1,QoeMetrix,Recievers)
                time_end = tm.time_ns()
                time_last = time_end-time_start
                #tl.write(str(time_last)+'\n')
                time_lp = time_lp+time_last
                #print(result)
                last_est = estimate
                #cluster work
                for i in range(usercount):
                    time_start = tm.time_ns()
                    output,low,high=cluster.kMeans(i,result[i],Recievers)
                    time_end = tm.time_ns()
                    time_last = time_end-time_start
                    #tc.write(str(time_last)+'\n')
                    time_cluster = time_cluster+time_last
                    for j in range(usercount):
                        init_bitrate_reciever[j][i]=output[j]
                    init_bitrate_sender[i]=low/3+high
                #print(init_bitrate_reciever) 
                #print(init_bitrate_sender)
                for reciever in Recievers:
                    #print(reciever.rebuffer)
                    reciever.setBitrate(init_bitrate_reciever[reciever.id])
                for sender in Senders:
                    sender.set_Bitrate(init_bitrate_sender[sender.id])
                error_sum = [[0]*usercount for row in range(usercount)]
            #run the online algrithm
            if(time%FB_GAP==1):
                #feedback
                estimate = []
                for i in range(usercount):
                    trace_to_estimate = downlink_trace[i][time:time+50]
                    estimate.append(algrithm.estimate(trace_to_estimate))
                change = []
                change.clear()
                for i in range(usercount):
                    traceA = downlink_trace[i][time+1500:time+1600]
                    traceB = downlink_trace[i][time:time+100]
                    change.append(algrithm.estimate(traceA)-algrithm.estimate(traceB))
                time_start = tm.time_ns()
                result,error_sum,lastbuffer = algrithm.bitratecontrol(Recievers,Senders,result,estimate,lastbuffer,lastrebuffer,FB_GAP,usercount,error_sum,change,k,j1)
                time_end = tm.time_ns()
                time_last = time_end-time_start
            # tf.write(str(time_last)+'\n')
                time_fba = time_fba+time_last
                for sender in Senders:
                    for reciever in Recievers:
                        lastrebuffer[sender.id][reciever.id] = reciever.rebuffer[sender.id]
                #print(result)
                for i in range(usercount):
                        time_start = tm.time_ns()
                        output,low,high=cluster.kMeans(i,result[i],Recievers)
                        time_end = tm.time_ns()
                        time_last = time_end-time_start
                        #tc.write(str(time_last)+'\n')
                        time_cluster = time_cluster+time_last
                        for j in range(usercount):
                            init_bitrate_reciever[j][i]=output[j]
                        init_bitrate_sender[i]=low/3+high
                        #print(low,high)
                #print(init_bitrate_reciever) 
                #print(init_bitrate_sender)
                for reciever in Recievers:
                    #print(reciever.rebuffer)
                    reciever.setBitrate(init_bitrate_reciever[reciever.id])
                for sender in Senders:
                    sender.set_Bitrate(init_bitrate_sender[sender.id])
        #print(time_cluster)
        #print(time_lp)
        #print(time_fba)
        #ts.write(str(time_cluster)+' '+str(time_lp)+' '+str(time_fba)+'\n')
        delay = delay/1000
        bbitrate=bbitrate/1000*30
        rrebuffer = rrebuffer/5
        jjitter =jjitter/1000
        qqoe = bbitrate-delay*20-jjitter-rrebuffer
        #print(delay)
        #print(bbitrate)
        #print(rrebuffer)
        #print(jjitter)
        daaata=[k,j1,qqoe]
        #print(daaata)
        #print(k)
        #print(j1)
        #df.write(str(bbitrate)+' '+str(delay*30)+' '+str(rrebuffer)+' '+str(jjitter)+' '+str(qqoe)+'\n')
        df.write(str(k)+' '+str(j1)+' '+str(qqoe)+'\n')