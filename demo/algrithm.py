import numpy as np
import pulp 
import math
def bitratecontrol(Recievers, Senders, bitrate,estimate,lastbuffer,lastrebuffer,type,usercount,error_sum,change,k,j):
    lastbuffer = [[0] * usercount for row in range(usercount)]
    for sender in Senders:
        for reciever in Recievers:
            if(sender.id!=reciever.id):
                quantity = 0
                for frame in reciever.buffer_index[sender.id]:
                    quantity = quantity + sender.static_frame_size[frame]      
                if len(reciever.buffer_index[sender.id])<5:
                    bufferEST = lastbuffer[sender.id][reciever.id]-(sum(bitrate for bitrate in reciever.bitrate)-estimate[reciever.id])/(usercount-1)*(type)
                else:
                    bufferEST = lastbuffer[sender.id][reciever.id]-(sum(bitrate for bitrate in reciever.bitrate)-estimate[reciever.id])/(usercount-1)*(type)
                if(bufferEST) <= 0:
                    bufferEST = 0
                #print(quantity-bufferEST)
                lastbuffer[sender.id][reciever.id] = quantity
                error_sum[sender.id][reciever.id] = error_sum[sender.id][reciever.id]+(quantity-bufferEST)
                temp=k*(quantity-bufferEST)/8000+j*error_sum[sender.id][reciever.id]/40000
                if(temp<0):
                    bitrate[sender.id][reciever.id] = bitrate[sender.id][reciever.id]+temp
                if(temp>0):
                    bitrate[sender.id][reciever.id] = bitrate[sender.id][reciever.id]+temp
                if bitrate[sender.id][reciever.id] < 0:
                    bitrate[sender.id][reciever.id] = 0.1
               # print(bitrate[sender.id][reciever.id])
    return bitrate,error_sum,lastbuffer
def offline_solve_LP(usercount,bandwidth_downlink_est,bandwidth_downlink_est_last,bandwidth_uplink_est,QoEMetrix,Recievers):
    jitter_direct = []
    for i in range(usercount):
        if bandwidth_downlink_est[i]>bandwidth_downlink_est_last[i]:
            jitter_direct.append(1)
        else:
            if  bandwidth_downlink_est[i]<bandwidth_downlink_est_last[i]:
                jitter_direct.append(-1)
            else:
                jitter_direct.append(0)

    bitrate = {}
    for i in range(usercount):
        bitrate[i] = [0]*usercount
    users = []
    for i in range(usercount):
        users.append(i)
    p = pulp.permutation(users,2)
    bitrate_index = [tuple(c) for c in p]
    bitrate_metrix = pulp.LpVariable.dicts('bitrate_table', bitrate_index, lowBound = 0.1)           
    prob = pulp.LpProblem('Opt', pulp.LpMaximize)
    prob += sum(QoEMetrix[pair[0]][pair[1]][0]*bitrate_metrix[pair]- QoEMetrix[pair[0]][pair[1]][1]*jitter_direct[pair[0]]*(bitrate_metrix[pair]-Recievers[pair[1]].bitrate[pair[0]])-0.3*QoEMetrix[pair[0]][pair[1]][1]*math.log10(10+Recievers[pair[1]].rebuffer[pair[0]]/3)
                -QoEMetrix[pair[0]][pair[1]][3]*(1/math.log2(3+2*len(Recievers[pair[1]].buffer_index[pair[0]])) )
                for pair in bitrate_index)
    for i in range(usercount):
        prob += sum(bitrate_metrix[pair] for pair in bitrate_index if pair[1] == i)<= 0.8*bandwidth_downlink_est[i]
    
    for i in range(usercount):
        for j in range(usercount):
            for k in range(usercount):
                prob += 0.6*sum(bitrate_metrix[pair] for pair in bitrate_index if pair[0]==k and (pair[1]==j or pair[1]==i))<=bandwidth_uplink_est[k]
    prob.solve()
    senderID = 0
    recieverID = 0
    for key in prob.variables():
        if senderID == recieverID:
            if recieverID<usercount-1:
                recieverID = recieverID + 1
            else:
                senderID = senderID + 1
                recieverID = 0
        bitrate[senderID][recieverID] = key.varValue
        if recieverID<usercount-1:
            recieverID = recieverID + 1
        else:
            senderID = senderID +1
            recieverID = 0
    #print(bitrate)
    return bitrate
def estimate(trace_to_estimate):
    sum = 0
    for i in trace_to_estimate:
        if i!=0:
            sum = sum + 1/i
    #print(sum)        
    harmonic_mean = len(trace_to_estimate)/sum
    #print(harmonic_mean)
    return harmonic_mean
def offline_solve(usercount,bandwidth_downlink_est,bandwidth_downlink_est_last,bandwidth_uplink_est,QoEMetrix,Recievers):
    bitrate = {}
    for i in range(usercount):
        bitrate[i] = [0]*usercount
    for i in range(usercount):
        for j in range(usercount):
            if i!=j:
                bitrate[i][j] = bandwidth_downlink_est[j]*QoEMetrix[i][j][0]/sum(QoEMetrix[k][j][0] for k in range(usercount))*0.8
            if len(Recievers[j].buffer_index[i])<5:
                bitrate[i][j] = bitrate[i][j]/2
            if bitrate[i][j]>bandwidth_uplink_est[i]:
                bitrate[i][j] = bandwidth_uplink_est[i]
            #print(bitrate[i][j]*30)
    return bitrate
            

        