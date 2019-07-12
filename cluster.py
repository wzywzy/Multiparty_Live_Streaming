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
    lastlowerBitrate = (minBitrate + randBitrate)/2
    lasthigherBitrate = (maxBitrate + randBitrate)/2
    newlowerBitrate  = 0.0
    newhigherBitrate = 0.0
    new_groupA = []
    new_groupB = []
    new_groupA.clear()
    new_groupB.clear()
    #print(lasthigherBitrate)
    #print(lastlowerBitrate)
    while(newlowerBitrate/(0.001+lastlowerBitrate)>1.2 or newlowerBitrate/(0.001+lastlowerBitrate)<0.83):
        lasthigherBitrate = newhigherBitrate
        lastlowerBitrate = newlowerBitrate
        for reciever in recievers:
            if reciever.id != id:
                if (abs(reciever.getQoe(id,bitrate_list[reciever.id])-reciever.getQoe(id,lastlowerBitrate))<abs(reciever.getQoe(id,bitrate_list[reciever.id])-reciever.getQoe(id,lastlowerBitrate))).all:
                    new_groupA.append(reciever.id)
                else:
                    new_groupB.append(reciever.id)
        if(len(new_groupA)*len(new_groupB)!=0):
            newlowerBitrate = sum(bitrate_list[reciever] for reciever in new_groupA)/len(new_groupA)
            newhigherBitrate = sum(bitrate_list[reciever] for reciever in new_groupB)/len(new_groupB)
        else:
            newlowerBitrate = (sum(bitrate_list[reciever] for reciever in new_groupA)+sum(bitrate_list[reciever] for reciever in new_groupB))/(len(new_groupA)+len(new_groupB))
            newhigherBitrate = newlowerBitrate
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

