'''
Created on 2018/07/23

@author: gong
'''
import time,datetime
import copy
import random
import numpy as np
import csv

from a_ReadRoadNetwork.readgeometry import *
from b_ODPackage.class_vehicle import *
from b_ODPackage.ReadOD import *
from c_TimeCalculation.time_calculation import *

from z_ExistingPackages.Dijkstra2 import *

#%%%%%%%%%%%%%%%%%%%%%for checking the results
outfile=open(r"D:\03Work during PD\31ERP2_in_COI\meso_by_python\output.csv","ab")#%%%%%%%%%%%%%%%%%%%%%for checking the results
writer=csv.writer(outfile)#%%%%%%%%%%%%%%%%%%%%%for checking the results

def check_position(p0,p1,p2):
    # this function checks the distance between point p0 to the line (connected from p1 to p2).
    # it is used to check whether the vehicle (update location is p0) is following the lane (line from p1 to p2)
    # if the distance is more than a threshold, it means the vehicle did not follow the lane and some error exists in the locate function.
    # input three points are in class of node {'coor-X':coor_X,'coor-Y':coor_Y,....}
    dummy_result=0
    
    return dummy_result

def locate(veh_id,curr_timestamp):
    # time_stamp is the current time, yyyy-mm-dd hh:mm:ss
    # this function update the vehicle location at current time
    # in case of receiving continuously instant GPS signal, it returns the map-matched coordinates(matched to the central line of lane (not included in this function yet). 
    # in case of a simulated circumstance, the current location is calculated based on the location of previous time stamp and the speed on related links. 
    pre_timestamp=get_pre_timestamp(curr_timestamp, timestep)# previous time stamp
    dummy_vanishing_veh=0# an indicator to show at current time stamp whether this vehicle will arrive its destination or not: 0, did not arrive; 1, arrived.
    #print "veh-id, current time, previous time", veh_id,time_stamp,pre_timestamp#****************for checking only
    #print "list-timestamps:", dic_vehicles[veh_id]['list-timestamps']#****************for checking only
    #print "locations are:", dic_vehicles[veh_id]['dic-locations']#****************for checking only
    #print "routes are:", dic_vehicles[veh_id]['dic-routes']#****************for checking only
    
    pre_location=dic_vehicles[veh_id]['dic-locations'][pre_timestamp]# location at previous stamp
    pre_route=dic_vehicles[veh_id]['dic-routes'][pre_timestamp]# best route at previous stamp,lane-based routes
    
    # two outputs of this function
    curr_location={}# initialize the location at current time stamp
        
    ###---------- calculate the location at current time stamp ------------###
    lane_id=pre_location['lane-id']    
    speed=dic_lanes[lane_id]['speed']
    #nodeid1=dic_lanes[lane_id]['node-id1']# node1 of the lane focused on
    nodeid2=dic_lanes[lane_id]['node-id2']# node2 of the lane focused on
    dist_to_id2=Dist(pre_location,dic_nodes[nodeid2])/1000.0# in km, make sure each item has a dictionary structure containing keys of "coor-X" and "coor-Y"
    time_to_id2=dist_to_id2*1.0/float(speed)*3600.0
    time_to_travel=copy.deepcopy(timestep)# the time that vehicle can move
    while time_to_travel>=time_to_id2:## check until vehicle cannot reach the end of a lane on the best path.
        if nodeid2==dic_vehicles[veh_id]['destination']:# this vehicle arrives its destination
            coor_X=dic_nodes[nodeid2]['coor-X']
            coor_Y=dic_nodes[nodeid2]['coor-Y']
            list_van_vehids.append(veh_id)# put its id into list of vanishing veh-ids
            dic_vehicles[veh_id]['end-timestamp']=curr_timestamp
            dic_vehicles[veh_id]['dic-speeds'][curr_timestamp]=speed
            # update its location to id2
            curr_location['coor-X']=coor_X
            curr_location['coor-Y']=coor_Y
            curr_location['lane-id']='' 
            dic_vehicles[veh_id]['dic-locations'][curr_timestamp]=curr_location
            dic_vehicles[veh_id]['dic-routes'][curr_timestamp]=''
            dic_vehicles[veh_id]['list-timestamps'].append(curr_timestamp)
            dummy_vanishing_veh=1
            break
        else:
            # if true, update lane to the next along the best route at previous time stamp;update the location of vehicle to the start node of updated lane (or end node of previous lane)
            time_to_travel=time_to_travel-time_to_id2
            lane_id=pre_route[lane_id]# update lane to the next lane of current lane along the best route at the previous time stamp
            dic_vehicles[veh_id]['list-laneid-used'].append(lane_id)
            pre_location={'coor-X':dic_nodes[nodeid2]['coor-X'],'coor-Y':dic_nodes[nodeid2]['coor-Y'],'lane-id':lane_id}# update the location of vehicle to the start node of next lane (end node of previous lane)
            #nodeid1=dic_lanes[lane_id]['node-id1']
            nodeid2=dic_lanes[lane_id]['node-id2']
            speed=dic_lanes[lane_id]['speed']
            dist_to_id2=Dist(pre_location,dic_nodes[nodeid2])/1000.0
            time_to_id2=dist_to_id2*1.0/float(speed)*3600             
    if dummy_vanishing_veh==0:
        # now veh-id cannot arrive node-id2 at the end of this simulation step        
        dic_vehicles[veh_id]['dic-speeds'][curr_timestamp]=speed#!!!!!!!!!!if the time step is long enough for vehicle to pass several links, this is the speed of the final link        
        #if speed<=1:
            #speed=1# set the min speed for traveling to avoid dead congestion
        X1=pre_location['coor-X']# coordinate X of previous location
        Y1=pre_location['coor-Y']# coordinate Y of previous location
        X2=dic_nodes[nodeid2]['coor-X']# coordinate X of end node of focused lane
        Y2=dic_nodes[nodeid2]['coor-Y']# coordinate Y of end node of focused lane
        coor_X=X1+(X2-X1)*time_to_travel/3600.0*speed*1000.0/Dist(dic_nodes[nodeid2],pre_location)# in meter, coordinate X of current position of vehicle
        coor_Y=Y1+(Y2-Y1)*time_to_travel/3600.0*speed*1000.0/Dist(dic_nodes[nodeid2],pre_location)# in meter, coordinate Y of current position of vehicle
        #cur_location={'coor-X':coor_X,'coor-Y':coor_Y,'lane-id':lane_id}
        curr_location['coor-X']=coor_X
        curr_location['coor-Y']=coor_Y
        curr_location['lane-id']=lane_id    
        # update the dictionaries of location and list of time stamps
        dic_vehicles[veh_id]['list-timestamps'].append(curr_timestamp)
        dic_vehicles[veh_id]['dic-locations'][curr_timestamp]=curr_location
        ###------------- best route is updated again if it decides to change lanes -----------------###
        # best route of current time stamp is set as the same as previous time stamp
        dic_vehicles[veh_id]['dic-routes'][curr_timestamp]=copy.deepcopy(pre_route)
    return()

def densityspeed(density,freespeed):
    # this function returns the speed on a lane when inputting a density
    # negative linear relationship between density and speed is used
    # additional parameters of free speed and jam  density are needed.
    if density>=jamdensity:# to avoid getting 0 or minus speed
        speed=0.001# km/h
    else:
        speed=freespeed*(1.0-1.0*density/jamdensity)    
 
    return speed

def updatelanes(curr_timestamp):
    # this function update features of all lanes in the dic_lanes, dic_graph_low and dic_graph_high at a time stamp.
    # the updated features include counts (the number of vehicles, pcu).
    # then the density, speed, and travel time are updated according to the counts.    
    
    # initialize the counts on each lane is 0
    for lane_id in dic_lanes.keys():
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
    
    # check which lane each running vehicle is on and count them    
    for veh_id in list_running_vehids:
        # check the vehicle type
        veh_type=dic_vehicles[veh_id]['veh-type']
        pcu=0
        if veh_type==0 or veh_type=='car':# car
            pcu=1.0
        elif veh_type==1 or veh_type=='bus':# bus
            pcu=3.5
        elif veh_type==2 or veh_type=='truck':# truck
            pcu=3.5
        else:
            print ("ERROR, no corresponding pcu value to the vehicle type")            
        lane_id=dic_vehicles[veh_id]['dic-locations'][curr_timestamp]['lane-id']# lane id where this running vehicle is on
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
    for lane_id in dic_lanes.keys():
        # update density, speed, travel-time in dic_lanes
        density=dic_lanes[lane_id]['density']=dic_lanes[lane_id]['counts']/dic_lanes[lane_id]['length']# density=counts/length, unit is pcu/km
        speed=dic_lanes[lane_id]['speed']=densityspeed(density,dic_lanes[lane_id]['free-speed'])# three input, real-time density, free-speed, jam density, unit is km/h
        travel_time=dic_lanes[lane_id]['travel-time']=dic_lanes[lane_id]['length']*3600.0/dic_lanes[lane_id]['speed']# real-time travel-time=length/real-time speed, unit is sec
        dic_lanes[lane_id]['dic-speeds'][curr_timestamp]=speed
        dic_lanes[lane_id]['dic-counts'][curr_timestamp]=dic_lanes[lane_id]['counts']
        dic_lanes[lane_id]['dic-densities'][curr_timestamp]=density        
        # obtain lane type and id1 and id2 to update the lane features in the other two lane dictionaries
        lane_type=dic_lanes[lane_id]['lane-type']
        id1=dic_lanes[lane_id]['node-id1']
        id2=dic_lanes[lane_id]['node-id2']
        # update density,speed,travel-time in two other lane dictionaries
        if lane_type==0:
            dic_graph_low[id1][id2]['density']=density
            dic_graph_low[id1][id2]['speed']=speed
            dic_graph_low[id1][id2]['travel-time']=travel_time
            dic_graph_low[id1][id2]['dic-speeds'][curr_timestamp]=speed
            dic_graph_low[id1][id2]['dic-counts'][curr_timestamp]=copy.deepcopy(dic_lanes[lane_id]['counts'])
            dic_graph_low[id1][id2]['dic-densities'][curr_timestamp]=density  
        elif lane_type==1:
            dic_graph_high[id1][id2]['density']=density
            dic_graph_high[id1][id2]['speed']=speed
            dic_graph_high[id1][id2]['travel-time']=travel_time
            dic_graph_high[id1][id2]['dic-speeds'][curr_timestamp]=speed
            dic_graph_high[id1][id2]['dic-counts'][curr_timestamp]=copy.deepcopy(dic_lanes[lane_id]['counts'])
            dic_graph_high[id1][id2]['dic-densities'][curr_timestamp]=density            
    return()

def best_route(veh_id,curr_timestamp):
    # this function search the best route for a vehicle at a time stamp, based on the lane features at previous time stamp
    # make sure this function is used after the previous function to obtain the latest travel time.    
    curr_location=dic_vehicles[veh_id]['dic-locations'][curr_timestamp]
    lane_id=curr_location['lane-id']
    nodeid1=dic_lanes[lane_id]['node-id1']    
    nodeid2=dic_lanes[lane_id]['node-id2']# it causes excluding the current lane (and this lanes' ids) in the best route search results. Manually include them in the results.  
    
    results={}
    D=dic_vehicles[veh_id]['destination']
    # search best route on low-slow lane-network
    D_low,P_low=shortestPathNode(dic_graph_low, nodeid2, D)
    best_route_lanes_l=convert_ppath_to_pathids(P_low,dic_graph_low,nodeid2,D)
    results['best-route-lanes-low']=best_route_lanes_l
    results['time-to-destination-low']=D_low[D]
    results['best-route-nodes-low']=P_low
    # add current lane information into the above results    
    next_nodeid=P_low[nodeid2]
    next_laneid=dic_graph_low[nodeid2][next_nodeid]['lane-id']
    results['best-route-nodes-low'][nodeid1]=nodeid2
    results['best-route-lanes-low'][lane_id]=next_laneid
    
    # search best route on high-fast lane-network
    D_high,P_high=shortestPathNode(dic_graph_high, nodeid2, D)
    best_route_lanes_h=convert_ppath_to_pathids(P_high, dic_graph_high, nodeid2, D)
    results['best-route-lanes-high']=best_route_lanes_h
    results['time-to-destination-high']=D_high[D]
    results['best-route-nodes-high']=P_high      
    # add current lane information into the above results
    next_nodeid=P_high[nodeid2]
    next_laneid=dic_graph_high[nodeid2][next_nodeid]['lane-id']
    results['best-route-nodes-high'][nodeid1]=nodeid2
    results['best-route-lanes-high'][lane_id]=next_laneid   
    return results

def decision(veh_id,curr_timestamp):
    # this function returns a result of whether to change to a faster and more expensive lane-network at a current time stamp after obtaining its current location.
    # this function is only used when the vehicle is not in the last section to its destination; this is an if-condition in the main program
    chan_lane=0# code of whether changing lanes to fast-expensive network: 1 is to change and 0 is not to change
    #start_time=dic_vehicles[veh_id]['start-timestamp']
    expect_endtime=dic_vehicles[veh_id]['expected-endtime']
    #print veh_id,dic_vehicles[veh_id]['start-timestamp'],dic_vehicles[veh_id]['origin'],dic_vehicles[veh_id]['destination'],"current time and expect end time are:", curr_timestamp,expect_endtime
    left_time_budget=Caltime(curr_timestamp,expect_endtime)
    best_route_results=best_route(veh_id, curr_timestamp)
    curr_location=dic_vehicles[veh_id]['dic-locations'][curr_timestamp]
    lane_id=curr_location['lane-id']
    nodeid2=dic_lanes[lane_id]['node-id2']
    speed=dic_vehicles[veh_id]['dic-speeds'][curr_timestamp]
    needed_time_low=best_route_results['time-to-destination-low']+Dist(curr_location,dic_nodes[nodeid2])/1000.0/speed*3600.0
    needed_time_high=best_route_results['time-to-destination-high']+Dist(curr_location,dic_nodes[nodeid2])/1000.0/speed*3600.0
    # check the left time budget and the value of time to decide the lane-changing probability
    if left_time_budget<needed_time_low:
        if dic_vehicles[veh_id]['value-time']>=median_value_time:
            dic_vehicles[veh_id]['lane-chan-p']=dic_vehicles[veh_id]['lane-chan-p']*2
            if dic_vehicles[veh_id]['lane-chan-p']>1:
                dic_vehicles[veh_id]['lane-chan-p']=1
        # conclude the decision based on the lane-changing probability
        if dic_vehicles[veh_id]['lane-chan-p']>=0.5:
            chan_lane=1# change lane
        else:
            chan_lane=0# do not change lane                
        if left_time_budget<needed_time_high:
            #######################print("even changing to the faster-expensive lane networks cannot arrive on time")
            chan_lane=0# do not change lane; need further study regarding loss
            dic_vehicles[veh_id]['lane-changed']=[9,curr_timestamp]# changing lane still cannot meet the time budget
    return chan_lane

def lane_change(veh_id,curr_timestamp):
    # update the current-lane id and best route as the vehicle changes to a fast-expensive lane network
    cur_location=dic_vehicles[veh_id]['dic-locations'][curr_timestamp]
    lane_id=cur_location['lane-id']
    id1=dic_lanes[lane_id]['node-id1']
    id2=dic_lanes[lane_id]['node-id2']
    fast_lane_id=dic_graph_high[id1][id2]['lane-id']
    low_lane_id=dic_graph_low[id1][id2]['lane-id']    
    best_route_results=best_route(veh_id, curr_timestamp)
    best_route_h=best_route_results['best-route-lanes-high']
    # one more pair should be included in the best_route_h, as lane-id-before-changing:next-lane-id has been included while lane-id-after-changing:next-lane-id has not been. the latter should also be included.
    next_lane_id=best_route_h[low_lane_id]
    best_route_h[fast_lane_id]=next_lane_id   
    
    ##################################################
    # lane-change is assumed to be instantly, which means the location and best-route should be updated simultaneously 
    # update the location and best route of the vehicle
    dic_vehicles[veh_id]['dic-locations'][curr_timestamp]['lane-id']=fast_lane_id
    dic_vehicles[veh_id]['dic-routes'][curr_timestamp]=best_route_h
    dic_vehicles[veh_id]['lane-type']=1
    dic_vehicles[veh_id]['lane-changed']=[1,curr_timestamp]
    dic_vehicles[veh_id]['list-laneid-used'].append(fast_lane_id)
    dic_vehicles[veh_id]['dic-speeds'][curr_timestamp]=dic_lanes[fast_lane_id]['speed']
    return()

###########=============== Main Program =================##################

# set the starting time stamp for simulation, 7am of running day
today_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:10]
simu_start_time_stamp=today_date+' '+'07:00:00'
# set whole simulation duration
total_steps=2000# 
# set time step used in the simulation, unit in seconds
timestep=1# 1 hour simulation is implemented, time-step is 1 seconds and totally 3600 steps are implemented

# set jam density used in this research
jamdensity=124# 200 pcu/mile=124 pcu/km. from:https://lost-contact.mit.edu/afs/eos.ncsu.edu/info/ce400_info/www2/flow1.html
# set/calculate the median of value-of-time used in the study
median_value_time=50# the median of value-of-time in SG, used to the check the person  
# set random seeds
random.seed(10)

# initialize vehicle-id; it is a global variable, as there may be many OD-matrix
vehicle_id=0# the first vehicle id is 1 and is increased subsequently with a step of 1


dic_nodes={}
dic_graph_low={}# all lanes belonging to the low fee type
dic_graph_high={}# all lanes belonging to the high fee type
dic_lanes={}

dic_vehicles={}# all vehicles; key is the vehicle id and a dictionary containing other features is used as the value. {vehid1:{'veh-type':veh_type,'max-speed':max_speed,....},vehid2:{... ...},vehid3:....} 
dic_gen_time_vehids={}# all vehicle-ids which are grouped by genration time stamp; key is a time stamp for generation, value is a list containing all vehicles' ids generated on that time stamp. {time1:[id1,id2,...],time2:[id5,id6,...],..}
list_running_vehids=[]# list containg all vehicle ids that are running on the network at current time stamp
list_gen_vehids=[]# list containing vehicle ids generated at current time stamp
#list_van_vehids=[]# list containing vehicle ids vanishing at current time stamp


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

writer.writerow(["following is the read node"])
for item in dic_nodes:
    writer.writerow([item,dic_nodes[item]])
writer.writerow(["****************************************************************************************************************"])

writer.writerow(["following is the read lanes"])
for item in dic_lanes:
    id1=dic_lanes[item]['node-id1']
    id2=dic_lanes[item]['node-id2']
    lane_ty=dic_lanes[item]['lane-type']
    writer.writerow(["dic-lanes",item, dic_lanes[item]])
    if lane_ty==0:
        writer.writerow(["dic-graph-low", dic_graph_low[id1][id2]['lane-id'],dic_graph_low[id1][id2]])
    else:
        writer.writerow(['dic-graph-high',dic_graph_high[id1][id2]['lane-id'],dic_graph_high[id1][id2]])
writer.writerow(["the geometry has been read completely"])
writer.writerow(["****************************************************************************************************************"])
########## read vehicles from OD-matrix in the csv files
folderpath=r"D:\03Work during PD\31ERP2_in_COI\meso_by_python\OD_data"# the folder where the OD files are stored
# obtain the OD matrices and simulation starting time from a series of csv files of traffic demand in OD pairs
OD_matrices=ReadOD(folderpath)
dic_vehicles,dic_gen_time_vehids=vehicle_gen(OD_matrices, 'uniform',vehicle_id,dic_graph_low,median_value_time,dic_nodes,dic_vehicles,dic_gen_time_vehids)

writer.writerow(["following is the read OD matrix"])
for item in OD_matrices:
    writer.writerow([OD_matrices[item]])
writer.writerow(["****************************************************************************************************************"])
writer.writerow(["following is the read vehicle at initial state"])
for item in dic_vehicles:
    writer.writerow([dic_vehicles[item]])
writer.writerow(["****************************************************************************************************************"])

writer.writerow(["following is the vehicles that should be generated at a pre-set time stamp"])

total_veh=0
for item in dic_gen_time_vehids:    
    writer.writerow([item,len(dic_gen_time_vehids[item]),dic_gen_time_vehids[item]])
    total_veh+=len(dic_gen_time_vehids[item])
print "total generated vehicles are:",total_veh,len(dic_vehicles)
writer.writerow(["total generated vehicles are:",total_veh,len(dic_vehicles)])
writer.writerow(["****************************************************************************************************************"])
        
######### update vehicles and geometry at every simulation step
# initialize current time stamp as the starting time stamp of the simulation
curr_timestamp=copy.deepcopy(simu_start_time_stamp)# string type
for i in range(0,total_steps):# each simulation step i    
    ####################################################################################################################
    #### generate vehicles,update vehicles' locations,  update vanishing vehicles, and finally update lane features ####
    ####################################################################################################################
    
    print "this is", i, "th step in simulation", curr_timestamp#%%%%%%%%%%%% for checking
    writer.writerow(["this is", i, "th step in simulation", curr_timestamp])
    #!!!!!!!!!!!!!!!!!!!!! calculation for this time stamp begins !!!!!!!!!!!!!!!!!!!!#
    # step1--------------------------------------------------------------------------------------------------------------------------------------------------------------
    ######**** regarding newly generated vehicles
    if dic_gen_time_vehids.has_key(curr_timestamp):# this time stamp generates vehicles           
        list_gen_vehids=copy.deepcopy(dic_gen_time_vehids[curr_timestamp])
        writer.writerow(["this time stamp generates vehicles. totally newly generated vehicles are ", len(list_gen_vehids)])
        # update their best route by previous time-stamp
        for veh_id in list_gen_vehids:# not generated at the initial time of simulation; need update their best route at first
            if curr_timestamp<>simu_start_time_stamp:
                writer.writerow(["following is the generated vehicles that are not generated at the simulation-starting time stamp"])
                O=dic_vehicles[veh_id]['origin']
                D=dic_vehicles[veh_id]['destination']
                D_low,P_low=shortestPathNode(dic_graph_low, O, D)
                best_route_lanes=convert_ppath_to_pathids(P_low,dic_graph_low,O,D)
                time_budget=D_low[D]

                # re-set and update the features of this vehicle
                dic_vehicles[veh_id]['dic-routes']={}
                dic_vehicles[veh_id]['dic-routes'][curr_timestamp]=best_route_lanes
                dic_vehicles[veh_id]['time-budget']=time_budget
                
                next_nodeid=P_low[O]
                lane_id=dic_graph_low[O][next_nodeid]['lane-id']                
                
                if time_budget>36000:
                    writer.writerow(["the time budget for",veh_id,"is more than 10h. ERROR"])
                    print "the time budget for",veh_id,"is more than 10h. ERROR"
                dic_vehicles[veh_id]['expected-endtime']=add_timestamp(curr_timestamp,time_budget)               
                #print O,D,results_best_route['best-route-nodes-low'],dic_vehicles[veh_id]['dic-locations'][curr_timestamp]
                next_nodeid=P_low[O]
                lane_id=dic_graph_low[O][next_nodeid]['lane-id']
                dic_vehicles[veh_id]['dic-locations'][curr_timestamp]['lane-id']=lane_id
                dic_vehicles[veh_id]['list-laneid-used'].append(lane_id)
                dic_vehicles[veh_id]['dic-speeds'][curr_timestamp]=dic_lanes[lane_id]['speed']
                # update list-of-used-lanes and dic-speeds
            writer.writerow(["the newly generated vehicles have the following features"])
            writer.writerow([dic_vehicles[veh_id]])
    else:# this time stamp does not generate vehicles
        list_gen_vehids=[]
        writer.writerow(["this time stamp does not generate new vehicles"])
    
    writer.writerow(["****************************************************************************************************************"])
    # step2-------------------------------------------------------------------------------------------------------------------------------------------------------------
    ######**** regarding the existing vehicles: update their locations by previous time stamp and make a decision, collecting the vanishing vehicles' ids simultaneously.
    list_van_vehids=[]# initialize the list-of-vanishing-vehicles as blank
    if len(list_running_vehids)>0:# there are vehicles running in the road network
        writer.writerow([curr_timestamp,"still has running vehicles on the network"])
        writer.writerow(["there are ",len(list_running_vehids)," vehicles running on the network"])
        print "there are ",len(list_running_vehids)," vehicles running on the network"
        writer.writerow(["their ids are",list_running_vehids])        
        for veh_id in list_running_vehids:                
            locate(veh_id, curr_timestamp)# obtain the current location of vehicles
            if dic_vehicles[veh_id]['lane-type']==0 and not veh_id in list_van_vehids:# only vehicles on slow lanes are making decisions
                veh_cur_laneid=dic_vehicles[veh_id]['dic-locations'][curr_timestamp]['lane-id']
                if dic_lanes[veh_cur_laneid]['node-id2']<>dic_vehicles[veh_id]['destination']:
                    dummy_chan_lane=decision(veh_id, curr_timestamp)
                    if dummy_chan_lane==1:
                        lane_change(veh_id, curr_timestamp)  # change to the fast-expensive lane
                else:
                    writer.writerow([veh_id, "is at the last section to its destination", dic_vehicles[veh_id]["destination"]])            
    else:
        writer.writerow([curr_timestamp,"does not have running vehicles on the network"])
    #print "vanishing vehicles are", list_van_vehids#%%%%%%%%%%%% for checking
    #print "running vehicles are", list_running_vehids#%%%%%%%%%%%% for checking
    writer.writerow(["after locating positions, there are ", len(list_van_vehids)," vanishing vehicles. their IDs are", list_van_vehids])
    print "after locating positions, there are ", len(list_van_vehids)," vanishing vehicles."
    # step3.1-----------------------------------------------------------------------------------------------------------------------------------------------------------
    #####**** regarding the list of running vehicles: remove the vanishing vehicle ids from the running vehicle ids
    writer.writerow(["now removing the vanishing vehicles from the running vehicles"])
    list_running_vehids=list(set(list_running_vehids).difference(set(list_van_vehids)))    
    writer.writerow(["after removing vanishing vehicles, the running vehicles are", len(list_running_vehids)])#%%%%%%%%%%%% for checking
    
    # step3.2-----------------------------------------------------------------------------------------------------------------------------------------------------------
    #####**** regarding the list of runnig vehicles: combine running vehicle ids with newly generated vehicle ids
    writer.writerow(["now combining the newly generated vehicles with the running vehicles"])
    list_running_vehids=list(set(list_gen_vehids).union(set(list_running_vehids)))
    #print "newly generated vehicles are", list_gen_vehids#%%%%%%%%%%%% for checking
    writer.writerow(["after combining with generated vehicles, the running vehicles are", len(list_running_vehids)])#%%%%%%%%%%%% for checking
    writer.writerow(["****************************************************************************************************************"])
    print "newly generated ", len(list_gen_vehids),"vehicles"
    print "after vanishing and generating, there are ", len(list_running_vehids)," vehicles on the network"
    
    # step4------------------------------------------------------------------------------------------------------------------------------------------------------------
    ######**** regarding the lanes: update the features
    writer.writerow(["now updating the lane features"])
    updatelanes(curr_timestamp)
    writer.writerow(["****************************************************************************************************************"])

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! move to the next time step in the simulation !!!!!!!!!!!!!!!!!!!!!!!!!!!!#
    writer.writerow(["move to the next simulation step"])
    curr_timestamp=add_timestamp(curr_timestamp, timestep)
    writer.writerow(["****************************************************************************************************************"])

    ############################################################################################################

######################################################################
######### output the statistics results  #############################
######################################################################
print "calculation finished; now output the results"
outfile_lane_features=open(r'D:\03Work during PD\31ERP2_in_COI\meso_by_python\outfile_lane_features.csv',"ab")
writer_lane_features=csv.writer(outfile_lane_features)

outfile_veh_features=open(r'D:\03Work during PD\31ERP2_in_COI\meso_by_python\outfile_veh_features.csv',"ab")
writer_veh_features=csv.writer(outfile_veh_features)
# order the features by time stamp
list_laneids=[]
list_vehids=[]
for lane_id in dic_lanes:
    list_laneids.append(lane_id)
for veh_id in dic_vehicles:
    list_vehids.append(veh_id)
list_laneids.sort
list_vehids.sort
list_timestamps=[]
for i in range(0,total_steps):
    timestamp=add_timestamp(simu_start_time_stamp, i)
    list_timestamps.append(timestamp)
columnheads1=["lane-id","lane-type"]+list_timestamps
columnheads2=["veh-id","veh-type"]+list_timestamps
columnheads3=["veh-id","veh-type","value-time","lane-chan-p","origin","destination","time-budget","start-time","expected-endtime","end-time","lane-changed"]
writer_veh_features.writerow(columnheads2)

# output features of lanes along the time stamps
writer_lane_features.writerow(["-----------------------following is the speeds of lanes along the time-stamps-----------------------"])
writer_lane_features.writerow(columnheads1)
for lane_id in list_laneids:
    row=[lane_id,dic_lanes[lane_id]['lane-type']]
    for timestamp in list_timestamps:
        row.append(dic_lanes[lane_id]['dic-speeds'][timestamp])
    writer_lane_features.writerow(row)
    
writer_lane_features.writerow(["-----------------------following is the counts of lanes along the time-stamps-----------------------"])
writer_lane_features.writerow(columnheads1)
for lane_id in list_laneids:
    row=[lane_id,dic_lanes[lane_id]['lane-type']]
    for timestamp in list_timestamps:
        row.append(dic_lanes[lane_id]['dic-counts'][timestamp])
    writer_lane_features.writerow(row)

writer_lane_features.writerow(["-----------------------following is the densities of lanes along the time-stamps-----------------------"])
writer_lane_features.writerow(columnheads1)
for lane_id in list_laneids:
    row=[lane_id,dic_lanes[lane_id]['lane-type']]
    for timestamp in list_timestamps:
        row.append(dic_lanes[lane_id]['dic-densities'][timestamp])
    writer_lane_features.writerow(row)

# output features of vehicles along the time stamps
print "now output the features of vehicles"
writer_veh_features.writerow(["-----------------------following is the speeds of vehicles along the time-stamps-----------------------"])
writer_veh_features.writerow(columnheads2)
for veh_id in list_vehids:
    row=[veh_id,dic_vehicles[veh_id]['veh-type']]
    for timestamp in list_timestamps:
        if dic_vehicles[veh_id]['dic-speeds'].has_key(timestamp):
            row.append(dic_vehicles[veh_id]['dic-speeds'][timestamp])
        else:
            row.append("")
    writer_veh_features.writerow(row)

writer_veh_features.writerow(["-----------------------following is the other features of vehicles----------------------"])
writer_veh_features.writerow(columnheads3)
for veh_id in list_vehids:
    row=[veh_id,dic_vehicles[veh_id]['veh-type'],dic_vehicles[veh_id]['value-time'],dic_vehicles[veh_id]['lane-chan-p'], \
         dic_vehicles[veh_id]['origin'],dic_vehicles[veh_id]['destination'],dic_vehicles[veh_id]['time-budget'], \
         dic_vehicles[veh_id]['start-timestamp'],dic_vehicles[veh_id]['expected-endtime'],dic_vehicles[veh_id]['end-timestamp'], \
         dic_vehicles[veh_id]['lane-changed']]
    writer_veh_features.writerow(row)

    
      




