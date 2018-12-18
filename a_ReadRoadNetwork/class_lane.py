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
        self.speed=float(record[6])# default value of real-time speed, in km/h, initialized as free-speed
        self.counts=0# the pcu on this lane
        self.density=0.1# default value of real-time density,
        self.traveltime=0.1# default value of travel time on this lane according to the density, in sec, initialized as free-travel-time
        self.charge=0.1# default charge of using this lane in the unit of dollar/km; this feature is used to store a dynamic charge according to density, in SGD/km
        
        self.dic_speeds={}# the instant speed at each simulation step: {timestamp1:speed1,timestamp2:speed2,timestamp3:speed3,...}
        self.dic_counts={}# the instant count at each simulation step: {timestamp1:count1,timestamp2:count2,timestamp3:count3,....}
        self.dic_densities={}# the instant density at each simulation step: {timestamp1:density1,timestamp2:density2,timestamp3:density3,...}  
        
import copy
def convert_ppath_to_pathids(dic_ppath,dic_graph,start_nodeid,end_nodeid):
    # this function converts the node-id-based shortest path output by function of shortestPathNode(G,start,end) to lane-id pair which will be used later.
    # input format:  {nodeid1:nodeid2,nodeid2:nodeid5,nodeid5:nodeid11,nodeid11:nodeid21,....}
    # output format: {laneid1:laneid12,laneid12:laneid21,laneid21:laneid3,...}
    # where lane1 is from node1 to node2, lane12 is from node2 to node5,...
    id1=start_nodeid
    list_laneids=[]# result in the process, list of lanes that compose the shortest path
    dic_routes={}# output
    #print "convert the node-pairs to list-of-lanes"
    if len(dic_ppath)>0:        
        while id1<>end_nodeid:
            id2=dic_ppath[id1]
            laneid=dic_graph[id1][id2]['lane-id']
            list_laneids.append(laneid)
            id1=copy.deepcopy(id2)
    #print "convert the list-of-lanes to dic-of-lanes"
    if len(list_laneids)>1:
        for i in range(0,len(list_laneids)-1):
            dic_routes[list_laneids[i]]=list_laneids[i+1]       
        
    # check the number of items in each dictionary and list
    #print "the number of node-pairs:", len(dic_ppath)
    #print "the number of lanes:     ", len(list_laneids)
    #print "the number of lane-pairs:", len(dic_routes)
    return dic_routes


'''

##The following section is to check the function named as convert_ppath_to_pathids

from z_ExistingPackages.Dijkstra2 import *
from a_ReadRoadNetwork.class_lane import *
from a_ReadRoadNetwork.class_node import *
from a_ReadRoadNetwork.readgeometry import *

dic_nodes={}
dic_graph_low={}# all lanes belonging to the low fee type
dic_graph_high={}# all lanes belonging to the high fee type
dic_lanes={}

########## read geometry from csv files
infile_node=open(r"D:\03Work during PD\31ERP2_in_COI\Sioux Falls network\nodes-SiouxFalls_gong.csv","r")
infile_node.readline()# jump the first row of column head
infile_lane=open(r"D:\03Work during PD\31ERP2_in_COI\Sioux Falls network\lanes-SiouxFalls_gong.csv","r")
infile_lane.readline()# jump the first row of column head

dic_nodes=ReadNodes(infile_node,dic_nodes)
dic_graph_high,dic_graph_low,dic_lanes=ReadLanes(infile_lane,dic_graph_high,dic_graph_low,dic_lanes)

# calculate the length of lanes
dic_graph_low =LengthCal(dic_graph_low, dic_nodes)
dic_graph_high=LengthCal(dic_graph_high,dic_nodes)
dic_lanes=LengthCal2(dic_lanes,dic_nodes)

O="5"
D="20"

dic_times,dic_nodes_on_routes=shortestPathNode(dic_graph_low, O, D)
print dic_nodes_on_routes

dic_lanes_on_routes=convert_ppath_to_pathids(dic_nodes_on_routes, dic_graph_low, O, D)
print dic_lanes_on_routes

'''        