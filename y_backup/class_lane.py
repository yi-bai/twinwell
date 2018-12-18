'''
Created on 2018/07/09

@author: gong
'''

class Lane(object):
    # as it is lane, it has only one direction; this is the different part from link
    def __init__(self,line):        
        #record=line.split(",") 
        record=line
        self.lanetype=int(record[0])# lane type evaluated as quick-charged-more lane and normal lane 
        self.laneid=str(record[1])# lane id when all lanes in the road network are put together
        self.nodeid1=str(record[2])# id of start node of this lane
        self.nodeid2=str(record[3])# id of end node of this lane
        self.linkid=str(record[4])# link id to which the lane belongs
        self.linktype=int(record[5])# link type evaluated as road ranking system, which leads to different free-flow speed
        self.length=0.01# length of the lane calculated from start node to end node,in km
        self.freespeed=float(record[6])# free flow speed of this lane,in km/h
        self.freetraveltime=float(record[7])# travel time of this lane under condition of free flow, in sec
        self.fixedcharge=float(record[8])# fixed charge of using this lane;in SGD/km
        self.speed=0.1# default value of real-time speed, in km/h
        self.counts=0# the pcu on this lane
        self.density=0.1# default value of real-time density,
        self.traveltime=0.1# default value of travel time on this lane according to the density, in sec
        self.charge=0.1# default charge of using this lane in the unit of dollar/km; this feature is used to store a dynamic charge according to density, in SGD/km
        

           
        
        
        