'''
Created on 2018/07/23

@author: gong
'''
import time,datetime
from e_VehiclePackage.e1_VehicleTypes import *
from a_ReadRoadNetwork.readgeometry import *
from z_ExistingPackages.Dijkstra2 import *
import copy
#from networkx.algorithms.bipartite.basic import density
#from jedi.debug import speed
import random
import numpy as np


# set time step used in the simulation, unit in seconds
timestep=1
# set jam density used in this research
jamdensity=124# 200 pcu/mile=124 pcu/km. from:https://lost-contact.mit.edu/afs/eos.ncsu.edu/info/ce400_info/www2/flow1.html
# set/calculate the median of value-of-time used in the study
median_value_time=50# the median of value-of-time in SG, used to the check the person  
# set random seeds
random.seed(10)
# set the time slot used in OD matrix, which is the time duration in which the OD is generated.
time_slot=5# unit is minute
# initialize vehicle-id; it is a global variable, as there may be many OD-matrix
vehicle_id=0# the first vehicle id is 1 and is increased subsequently with a step of 1


dic_nodes={}
dic_graph_low={}# all lanes belonging to the low fee type
dic_graph_high={}# all lanes belonging to the high fee type
dic_lanes={}
list_vehids=[]# all vehicle ids at current time stamp
dic_vehicles={}# all vehicles; key is the vehicle id and a dictionary containing other features is used as the value. {vehid1:{'veh-type':veh_type,'max-speed':max_speed,....},vehid2:{... ...},vehid3:....} 



def locate(vehicle,time_stamp):
    # time_stamp is the current time
    # this function update the vehicle location at current time
    # in case of receiving continuously instant GPS signal, it returns the map-matched coordinates(matched to the central line of lane (not included in this function yet). 
    # in case of a simulated circumstance, the current location is calculated based on the location of previous time stamp and the speed on related links. 
    pre_timestamp=get_pre_timestamp(time_stamp, timestep)# previous time stamp
    pre_location=vehicle.dic_locatins[pre_timestamp]# location at previous stamp
    pre_route=vehicle.dic_routes[pre_timestamp]# best route at previous stamp
    
    # two outputs of this function
    cur_location={}# initialize the location at current time stamp
    cur_route={}# initialize the best route at current time stamp
    
    ###---------- calculate the location at current time stamp ------------###
    lane_id=pre_location['lane-id']
    speed=dic_lanes[lane_id]['speed']
    nodeid1=dic_lanes[lane_id]['node-id1']# node1 of the lane focused on
    nodeid2=dic_lanes[lane_id]['node-id2']# node2 of the lane focused on
    dist_to_id2=Dist(pre_location,dic_nodes[nodeid2])# make sure each item has a dictionary structure containing keys of "coor-X" and "coor-Y"
    time_to_id2=dist_to_id2/float(speed)
    time_to_travel=copy.deepcopy(timestep)# the time that vehicle can move
    while time_to_id2<time_to_travel:# check until vehicle cannot reach the end of a lane on the best path.
        # if true, update lane to the next on the best route at previous time stamp;update the location of vehicle to the start node of updated lane (or end node of previous lane)
        time_to_travel=time_to_travel-time_to_id2
        lane_id=pre_route[lane_id]# update lane to the next lane of current lane along the best route at the previous time stamp
        location={'coor-X':dic_nodes[nodeid2]['coor-X'],'coor-Y':dic_nodes[nodeid2]['coor-Y'],'lane-id':lane_id}# update the location of vehicle to the start node of next lane (end node of previous lane)
        nodeid1=dic_lanes[lane_id]['node-id1']
        nodeid2=dic_lanes[lane_id]['node-id2']
        speed=dic_lanes[lane_id]['speed']
        dist_to_id2=Dist(location,dic_nodes[nodeid2])
        time_to_id2=dist_to_id2/float(speed)
    X1=dic_nodes[nodeid1]['coor-X']# coordinate X of start node of focused lane (same lane of previous time stamp or the updated lane along the best route depending on while)(same as following three)
    Y1=dic_nodes[nodeid1]['coor-Y']# coordinate Y of start node of focused lane
    X2=dic_nodes[nodeid2]['coor-X']# coordinate X of end node of focused lane
    Y2=dic_nodes[nodeid2]['coor-Y']# coordinate Y of end node of focused lane
    coor_X=X1+(X2-X1)*time_to_travel*speed/Dist(dic_nodes[nodeid2],dic_nodes[nodeid1])# coordinate X of current position of vehicle
    coor_Y=Y1+(Y2-Y1)*time_to_travel*speed/Dist(dic_nodes[nodeid2],dic_nodes[nodeid1])# coordinate Y of current position of vehicle
    #cur_location={'coor-X':coor_X,'coor-Y':coor_Y,'lane-id':lane_id}
    cur_location['coor-X']=coor_X
    cur_location['coor-Y']=coor_Y
    cur_location['lane-id']=lane_id
    ###------------- calculate the best route at current time stamp -----------### 
    # update the dictionary of best route based on the current lane type is slow-cheap or fast-expensive 
    # it needs to update again after the vehicle making a decision whether to change the lane
    if dic_lanes[lane_id]['lane-type']==0:
        D_low,P_low=Dijkstra(dic_graph_low, dic_nodes[nodeid2], dic_nodes[vehicle.destination])
        cur_route=P_low
    elif dic_lanes[lane_id]['lane-type']==1:
        D_high,P_high=Dijkstra(dic_graph_high, dic_nodes[nodeid2], dic_nodes[vehicle.destination])
        cur_route=P_high
    else:
        print ("sth wrong with the lane type of current lane, either 0 or 1 is required")    
    
    # update the dictionaries of location and best route
    vehicle.list_timestamp.append(time_stamp)
    vehicle.dic_locations[time_stamp]=cur_location
    vehicle.dic_routes[time_stamp]=cur_route
    return(vehicle)
def arrive(vehicle,timestamp):
    #this function returns 1 indicating the vehicle has already arrived its destination.
    result=0
    
    return result
def densityspeed(density,freespeed):
    # this function returns the speed on a lane when inputting a density
    # negative linear relationship between density and speed is used
    # additional parameters of free speed and jam  density are needed.
    speed=freespeed*(1.0-1.0*density/jamdensity)    
    return(speed)

def updatelanes(time_stamp):
    # this function update features of lanes in the dic_lanes, dic_graph_low and dic_graph_high at a time stamp.
    # the updated features include counts (the number of vehicles, pcu).
    # then the density, speed, and travel time are updated according to the counts.    
    # initialize the counts on each lane is 0
    for lane_id in dic_lanes:
        dic_lanes[lane_id]['counts']=0
        id1=dic_lanes[lane_id]['node-id1']
        id2=dic_lanes[lane_id]['node-id2']
        lane_type=dic_lanes[lane_id]['lane-type']
        if lane_type==0:
            dic_graph_low[id1][id2]['counts']=0
        elif lane_type==1:
            dic_graph_high[id1][id2]['counts']=0
        else:
            print('sth wrong when initialize counts on the lanes')
    # check which lane each vehicle is on and count    
    for veh_id in list_vehids:
        # check the vehicle type
        veh_type=dic_vehicles[veh_id]['veh-type']
        pcu=0
        if veh_type==0:# car
            pcu=1
        elif veh_type==1:# bus
            pcu=3.5
        elif veh_type==2:# truck
            pcu=3.5
        else:
            print ("no corresponding pcu value is found")            
        lane_id=dic_vehicles[veh_id].dic_locations[time_stamp]['lane-id']# lane id where vehicle is on
        dic_lanes[lane_id]['counts']+=pcu
        lane_type=dic_lanes[lane_id]['lane-type']
        id1=dic_lanes[lane_id]['node-id1']
        id2=dic_lanes[lane_id]['node-id2']        
        if lane_type==0:
            dic_graph_low[id1][id2]['counts']+=pcu
        elif lane_type==1:
            dic_graph_high[id1][id2]['counts']+=pcu
        else:
            print("sth wrong when counting the vehicles on the lanes")
    # update the density and speed on each lane based on the counts on the lane
    for lane_id in dic_lanes:
        # update density, speed, travel-time in dic_lanes
        density=dic_lanes[lane_id]['density']=dic_lanes[lane_id]['counts']/dic_lanes[lane_id]['length']# density=counts/length, unit is 
        speed=dic_lanes[lane_id]['speed']=densityspeed(dic_lanes[lane_id]['density'],dic_lanes[lane_id]['free-speed'])# three input, real-time density, free-speed, jam density
        travel_time=dic_lanes[lane_id]['travel-time']=dic_lanes[lane_id]['length']/dic_lanes[lane_id]['speed']# real-time travel-time=length/real-time speed, unit is
        # obtain lane type and id1 and id2 to update the lane features in the other two lane dictionaries
        lane_type=dic_lanes[lane_id]['lane-type']
        id1=dic_lanes[lane_id]['node-id1']
        id2=dic_lanes[lane_id]['node-id2']
        # update density,speed,travel-time in two other lane dictionaries
        if lane_type==0:
            dic_graph_low[id1][id2]['density']=density
            dic_graph_low[id1][id2]['speed']=speed
            dic_graph_low[id1][id2]['travel-time']=travel_time
        elif lane_type==1:
            dic_graph_high[id1][id2]['density']=density
            dic_graph_high[id1][id2]['speed']=speed
            dic_graph_high[id1][id2]['travel-time']=travel_time
    return()

def best_route(vehicle,time_stamp):
    # this function search the best route for a vehicle at a time stamp, based on the lane features and location of vehicle at the time stamp
    # make sure this function is used after the previous function to obtain the latest travel time.
    cur_location=vehicle.dic_locations[time_stamp]
    lane_id=cur_location['lane-id']
    #nodeid1=dic_lanes[lane_id]['node-id1']
    nodeid2=dic_lanes[lane_id]['node-id2']
    results={}
    # search best route on low-slow lane-network
    D_low,P_low=Dijkstra(dic_graph_low, dic_nodes[nodeid2], dic_nodes[vehicle.destination])
    results['best-route-low']=P_low# best route is another dictionary
    results['time-to-destination-low']=D_low[dic_nodes[vehicle.destination]]
    # search best route on high-fast lane-network
    D_high,P_high=Dijkstra(dic_graph_high, dic_nodes[nodeid2], dic_nodes[vehicle.destination])
    results['best-route-high']=P_high
    results['time-to-destination-high']=D_high[dic_nodes[vehicle.destination]]      
    return(results)

def decision(vehicle,time_stamp):
    # this function returns a result of whether to change to a faster and more expensive lane-network at a given time-stamp
    chan_lane=0# code of whether changing lanes to fast-expensive network: 1 is to change and 0 is not to change
    start_time=vehicle.starttime
    expect_endtime=vehicle.expected_endtime
    time_budget=vehicle.time_budget
    left_time_budget=Caltime(time_stamp,expect_endtime)
    best_route_results=best_route(vehicle, time_stamp)
    needed_time_low=best_route_results['time-to-destination-low']
    needed_time_high=best_route_results['time-to-destination-high']
    # check the left time budget and the value of time to decide the lane-changing probability
    if left_time_budget<needed_time_low:
        if vehicle.value_time>=median_value_time:
            vehicle.lane_chan_probability=vehicle.lane_chan_probability*2
            if vehicle.lane_chan_probability>1:
                vehicle.lane_chan_probability=1
    elif left_time_budget<needed_time_high:
        print("even changing to the faster-expensive lane networks cannot arrive on time")
    # conclude the decision based on the lane-changing probability
    if vehicle.lane_chan_probability>=0.5:
        chan_lane=1
    else:
        chan_lane=0        
    return(chan_lane)

def get_pre_timestamp(cur_time,timestep):
    # this function returns the previous time stamp which is "timestep" less than current time stamp
    # cur_time is the current time stamp, in the format of hh:mm:ss
    today=datetime.datetime.now().date()# date of today, used to combine with current time to make a complete combination of date and time
    cur_time=str(today)+" "+str(cur_time)# date + time
    cur_time=datetime.datetime.strptime(cur_time,"%Y-%m-%d %H:%M:%S")# change the type to datetime from string    
    timestep=float(timestep)    
    timestep=datetime.timedelta(seconds=timestep)
    pre_timestamp=cur_time-timestep
    pre_timestamp=str(pre_timestamp)[11:]# remove the date and just leave the time
    return pre_timestamp


###########=============== Main Program =================##################
########## read geometry from csv files
infile_node=open(r"D:\03Work during PD\31ERP2_in_COI\Sioux Falls network\nodes-SiouxFalls_gong.csv","r")
infile_node.readline()# jump the first row of column head
infile_lane=open(r"D:\03Work during PD\31ERP2_in_COI\Sioux Falls network\lanes-SiouxFalls_gong.csv","r")
infile_lane.readline()# jump the first row of column head

ReadNodes(infile_node)
ReadLanes(infile_lane)

# calculate the length of lanes
dic_graph_low =LengthCal(dic_graph_low, dic_nodes)
dic_graph_high=LengthCal(dic_graph_high,dic_nodes)
dic_lanes=LengthCal2(dic_lanes)

########## read vehicles from OD-matrix in the csv files



######### update vehicles and geometry at every simulation step



######### output the statistics results




