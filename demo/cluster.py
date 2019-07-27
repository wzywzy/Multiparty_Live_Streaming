import numpy as np

# k-means 聚类算法
def kMeans(id,bitrate_list,recievers):
    random = np.random.RandomState(0)
    one_way_bitrate = sum(bitrate for bitrate in bitrate_list)/5
    maxBitrate = max(bitrate_list)
    minBitrate = maxBitrate
    for i in bitrate_list:
        if i>0:
            if i<minBitrate:
                minBitrate = i
    randBitrate = (minBitrate+maxBitrate)/2
    lastlowerBitrate = minBitrate
    lasthigherBitrate = maxBitrate
    newlowerBitrate  = 0.0
    newhigherBitrate = 0.0
    new_groupA = []
    new_groupB = []
    new_groupA.clear()
    new_groupB.clear()
    #print(lasthigherBitrate)
    #print(lastlowerBitrate)
    while(newlowerBitrate/(0.001+lastlowerBitrate)>1.3 or newlowerBitrate/(0.001+lastlowerBitrate)<0.8):
        
        for reciever in recievers:
            if reciever.id != id:
                if (abs(bitrate_list[reciever.id]-lastlowerBitrate)<abs(bitrate_list[reciever.id]-lasthigherBitrate)):
                    new_groupA.append(reciever.id)
                else:
                    new_groupB.append(reciever.id)
        lasthigherBitrate = newhigherBitrate
        lastlowerBitrate = newlowerBitrate
        if(len(new_groupA)*len(new_groupB)!=0):
            newlowerBitrate = sum(bitrate_list[reciever] for reciever in new_groupA)/len(new_groupA)
            newhigherBitrate = sum(bitrate_list[reciever] for reciever in new_groupB)/len(new_groupB)
        else :
            if(len(new_groupB)==0):
                newhigherBitrate = newlowerBitrate
                newlowerBitrate = (sum(bitrate_list[reciever] for reciever in new_groupA)+sum(bitrate_list[reciever] for reciever in new_groupB))/(len(new_groupA)+len(new_groupB))
            if(len(new_groupA)==0):
                newlowerBitrate = newhigherBitrate
                newhigherBitrate = (sum(bitrate_list[reciever] for reciever in new_groupA)+sum(bitrate_list[reciever] for reciever in new_groupB))/(len(new_groupA)+len(new_groupB))
        #print(lasthigherBitrate)
        #print(newlowerBitrate)
    result = []
    for i in recievers:
        if i.id == id:
            result.append(0)
        else:
            if i in new_groupA:
                result.append(newlowerBitrate)
            else:
                result.append(newhigherBitrate)
    return result,newlowerBitrate,newhigherBitrate

