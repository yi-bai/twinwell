'''
Created on 2018/07/10

@author: gong
'''
from class_node import Node
from class_lane import Lane
import csv

def Dist(p1,p2):
    # the input two points are nodes defined with same features in node class
    return(((p1['coor-X']-p2['coor-X'])**2+ (p1['coor-Y']-p2['coor-Y'])**2)**(0.5))   
# dictionary to store the information of all nodes
# key is the node id, value is another dictionary which contains features of the node
# an example in the dictionary is as follows: 
# node-id:{node-type:value0,coordinate-type:value1, coor-X:value2, coor-Y:value3]
dic_nodes={}

# dictionary to store the information of all lanes
# one dictionary is a network composed by a certain type of lanes
# key is the lane id, value is another dictionary whose key is the starting node id and value is the third dictionary containing features of lane
# an example in the dictionary is as follows:
# node1-id:{node2-id:{lane-type:value0,lane-id:value1,link-id:value2,link-type:value3,length:value4,free-speed:value5, \
#           free-time:value6,speed:value7,density:value8,travel-time:value9,fixed-charge:value10, \
#           dynamic-charge:value11},node2-id2:{...},...}
# this structure of dictionary only consider only one lane for one lane-type inside a link;otherwise, one more dictionary is needed.
dic_graph_low={}# all lanes belonging to the low fee type
dic_graph_high={}# all lanes belonging to the high fee type

# another dictionary of lane is defined as follows: key is lane id, the value is another dictionary which include other features of the lane
dic_lanes={}
# two types of dictionaries of lane should be updated simultaneously.


def ReadNodes(nodefile):
    # this function reads nodes from csv file to the dict_nodes
    reader=csv.reader(nodefile)
    for row in reader:
        node=Node(row)
        if not dic_nodes.has_key(node.nodeid):
            dic_nodes[node.nodeid]={'node-type':node.nodetype,'coor-type':node.coortype,'coor-X':node.coorX,'coor-Y':node.coorY}
        else:
            print("duplicate node id, ATTENTION")
    return dic_nodes

def ReadLanes(lanefile):
    # this function reads lanes from csv file to the dic_graph_low and dic_graph_high depending on the lane type
    reader=csv.reader(lanefile)
    count0=0# used to check whether the total number of read lanes is equal to the csv file
    count1=0
    for row in reader:
        lane=Lane(row)
        # include lanes to dic_graph_low and dic_graph_high depending on the lane category
        if int(lane.lanetype)==0:# the low-speed-type lane
            if dic_graph_low.has_key(lane.nodeid1):
                if not dic_graph_low[lane.nodeid1].has_key(lane.nodeid2):
                    print(lane.nodeid1,lane.nodeid2)
                    count0+=1
                    dic_graph_low[lane.nodeid1][lane.nodeid2]={'lane-type':lane.lanetype,'lane-id':lane.laneid,'link-id':lane.linkid, \
                                                               'link-type':lane.linktype,'length':lane.length,'free-speed':lane.freespeed, \
                                                               'free-time':lane.freetraveltime,'speed':lane.speed,'density':lane.density, \
                                                               'travel-time':lane.traveltime,'fixed-charge':lane.fixedcharge, \
                                                               'dynamic-charge':lane.charge,'counts':lane.counts}
                else:
                    print('duplicate lanes for low speed type, ATTENTION',lane.nodeid1,lane.nodeid2)
            else:
                count0+=1
                dic_graph_low[lane.nodeid1]={}
                dic_graph_low[lane.nodeid1][lane.nodeid2]={'lane-type':lane.lanetype,'lane-id':lane.laneid,'link-id':lane.linkid, \
                                                           'link-type':lane.linktype,'length':lane.length,'free-speed':lane.freespeed, \
                                                           'free-time':lane.freetraveltime,'speed':lane.speed,'density':lane.density, \
                                                           'travel-time':lane.traveltime,'fixed-charge':lane.fixedcharge, \
                                                           'dynamic-charge':lane.charge,'counts':lane.counts}    
        elif int(lane.lanetype)==1:
            if dic_graph_high.has_key(lane.nodeid1):
                if not dic_graph_high[lane.nodeid1].has_key(lane.nodeid2):
                    print(lane.nodeid1,lane.nodeid2)
                    count1+=1
                    dic_graph_high[lane.nodeid1][lane.nodeid2]={'lane-type':lane.lanetype,'lane-id':lane.laneid,'link-id':lane.linkid, \
                                                               'link-type':lane.linktype,'length':lane.length,'free-speed':lane.freespeed, \
                                                               'free-time':lane.freetraveltime,'speed':lane.speed,'density':lane.density, \
                                                               'travel-time':lane.traveltime,'fixed-charge':lane.fixedcharge, \
                                                               'dynamic-charge':lane.charge,'counts':lane.counts}
                else:
                    print('duplicate lanes for high speed type, ATTENTION',lane.nodeid1,lane.nodeid2)
            else:
                count1+=1
                dic_graph_high[lane.nodeid1]={}
                dic_graph_high[lane.nodeid1][lane.nodeid2]={'lane-type':lane.lanetype,'lane-id':lane.laneid,'link-id':lane.linkid, \
                                                           'link-type':lane.linktype,'length':lane.length,'free-speed':lane.freespeed, \
                                                           'free-time':lane.freetraveltime,'speed':lane.speed,'density':lane.density, \
                                                           'travel-time':lane.traveltime,'fixed-charge':lane.fixedcharge, \
                                                           'dynamic-charge':lane.charge,'counts':lane.counts}              
        # include the lane into dic_lanes
        if dic_lanes.has_key(lane.laneid):
            print('duplicate lane ids, error in the data set')
        else:
            dic_lanes[lane.laneid]={'lane-type':lane.lanetype,'node-id1':lane.nodeid1,'node-id2':lane.nodeid2, 'link-id':lane.linkid, \
                                   'link-type':lane.linktype,'length':lane.length,'free-speed':lane.freespeed, \
                                   'free-time':lane.freetraveltime,'speed':lane.speed,'density':lane.density, \
                                   'travel-time':lane.traveltime,'fixed-charge':lane.fixedcharge, \
                                   'dynamic-charge':lane.charge,'counts':lane.counts}
    # check the number of items in the dictionaries
    print('count of 1st type lane is ',count0)
    print("count of 2nd type lane is ",count1)
    return dic_graph_high,dic_graph_low,dic_lanes

def LengthCal(dic_graph,dic_nodes):
    # this function calculate and update the length of lanes inside a graph with the node id coordinates
    # calculate the length of lanes in dic_graph which uses node-ids as the key 
    for key1 in dic_graph:
        for key2 in dic_graph[key1]:
            dic_graph[key1][key2]['length']=Dist(dic_nodes[key1],dic_nodes[key2])/1000.0# coordinates are in meter; length is in km
            dic_graph[key1][key2]['free-time']=dic_graph[key1][key2]['length']*1.0/dic_graph[key1][key2]['free-speed']*3600.0# travel time is in seconds
    return(dic_graph)

def LengthCal2(dic_lanes):
    # this function calculate and update the length of lanes inside a graph with the node id coordinates 
    # calculate the length of lanes in dic_lanes which uses lane-id as the key
    for key1 in dic_lanes:
        dic_lanes[key1]['length']=Dist(dic_nodes[dic_lanes[key1]['node-id1']],dic_nodes[dic_lanes[key1]['node-id2']])/1000.0# coordinates are in meter; length is in km
        dic_lanes[key1]['free-time']=dic_lanes[key1]['length']*1.0/dic_lanes[key1]['free-speed']*3600.0# travel time is in seconds
    return(dic_lanes)


''''
# import csv files where the node and lane data are stored
infile_node=open(r"D:\03Work during PD\31ERP2_in_COI\Sioux Falls network\nodes-SiouxFalls_gong.csv","r")
infile_node.readline()# jump the first row of column head
infile_lane=open(r"D:\03Work during PD\31ERP2_in_COI\Sioux Falls network\lanes-SiouxFalls_gong.csv","r")
infile_lane.readline()# jump the first row of column head

dic_nodes=ReadNodes(infile_node)
dic_graph_high,dic_graph_low,dic_lanes=ReadLanes(infile_lane)

# calculate the length of lanes
dic_graph_low =LengthCal(dic_graph_low, dic_nodes)
dic_graph_high=LengthCal(dic_graph_high,dic_nodes)
dic_lanes=LengthCal2(dic_lanes)

# check whether the length is correctly 
for key1 in dic_graph_low:# for any node-id1
    for key2 in dic_graph_low[key1]:# for any node-id2
        print dic_graph_low[key1][key2]
        print dic_graph_high[key1][key2]
        print dic_lanes[dic_graph_low[key1][key2]['lane-id']]
'''        