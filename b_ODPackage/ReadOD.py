'''
Created on 2018/07/02
This module is used to read the OD matrices from csv files.

csv file of OD matrix should be named as the time slot with beginning and ending time;
names following the above rule is to suit the loading of traffic demand to the road network;
all csv files for one road network or a possible scenario should be put in one folder.

The format of OD demand in the csv file consists of the following columns:
time slot, vehicle type, origin ID, destination ID,vehicle volume

currently, we use a time slot of 5 minutes. vehicles generated during this time slot are put randomly onto the road network.

done and checked on 2018/7/4 

module of generating vehicles is also included in this module as vehicle-generation is just the next step of reading OD-matrix; and these two modules cannot be separated.

@author: gong
'''
import time,datetime
import random
random.seed(10)
from class_vehicle import *
import numpy as np
from z_ExistingPackages.Dijkstra2 import *
from c_TimeCalculation.time_calculation import *
from math import ceil,floor
import csv
import os
from a_ReadRoadNetwork.class_lane import *



def ReadOD(folderpath):
    
    list_file_names=os.listdir(folderpath)#return a list containing all names of all files in the folder(folderpath)
    #print list_file_names
    dic_OD={}
    for eachfile in list_file_names:
        print eachfile
        each_file_path=os.path.join('%s%s%s' % (folderpath,"/", eachfile))#each path+file
        infile=open(each_file_path,"r")
        infile.readline()#jump the first row in the csv file, which is the column head
        reader=csv.reader(infile)        
        for row in reader:
            #print row
            timeslot   =row[0]#time slot, every 5 minute
            vehicle    =row[1]#vehicle type
            origin     =row[2]#O,node ID
            destination=row[3]#D,node ID
            volume     =int(row[4])#vehicle volume from O to D.
            OD=origin+"_to_"+destination
            #print OD
            if dic_OD.has_key(timeslot):
                if dic_OD[timeslot].has_key(OD):
                    if dic_OD[timeslot][OD].has_key(vehicle):
                        print("ATTENTION:duplicate vehicle type for same OD during same time slot")
                        dic_OD[timeslot][OD][vehicle]+=volume
                    else:                        
                        dic_OD[timeslot][OD][vehicle]=volume
                else:                    
                    dic_OD[timeslot][OD]={}
                    dic_OD[timeslot][OD][vehicle]=volume
            else:
                dic_OD[timeslot]={}
                dic_OD[timeslot][OD]={}
                dic_OD[timeslot][OD][vehicle]=volume
        #print dic_OD.keys()
    return dic_OD

             
def obtain_time_stamp(timeslot):
    # this function converts the time-slot (in string) to time stamps of the start and ending of the time-slot
    # an example of the original format of time-slot can be '7.10-7.14' which means time slot from 7:10:00-7:14:59, totally 300 seconds
    # this function is used to extract 'yyyy-mm-dd 7:10:00' and 'yyyy-mm-dd 7:14:59' from the string of '7.10-7.14'
    # separate the string into two firstly
    split_times=timeslot.split("-")
    start=split_times[0]
    ending=split_times[-1]
    split_start=start.split(".")
    hour_start=split_start[0]
    minu_start=split_start[-1]
    split_ending=ending.split(".")
    hour_end=split_ending[0]
    minu_end=split_ending[-1]
    start_time=hour_start+":"+minu_start+":"+"00"
    end_time=hour_end+":"+minu_end+":"+"59"
    today=datetime.datetime.now().date()# date of today, used to combine with current time to make a complete combination of date and time
    start=str(today)+" "+str(start_time)# date + time
    start=datetime.datetime.strptime(start,"%Y-%m-%d %H:%M:%S")# change the type to datetime from string
    ending=str(today)+" "+str(end_time)
    ending=datetime.datetime.strptime(ending,"%Y-%m-%d %H:%M:%S")  
    return str(start)[:19],str(ending)[:19] # returned values are in string type

def obtain_O_and_D(OD_label):
    # this function returns the label of O and label D, the code ids of origin and destination when inputting a OD label which is the key of a series of OD-values
    # the output is a list containing origin code ID and destination code ID, both of which are strings
    split_od_label=OD_label.split("_to_")
    O=split_od_label[0]
    D=split_od_label[1]
    return O,D# strings

def vehicle_maxspeed(veh_type):
    # this function returns the max speed at random value during a given interval
    random.seed(10)
    max_speed_interval_car=[70,80]
    max_speed_interval_truck=[50,70]
    max_speed_interval_bus=[40,60]
    max_speed=0
    if veh_type=="car":
        max_speed=random.randint(max_speed_interval_car[0],max_speed_interval_car[1])
    elif veh_type=="truck":
        max_speed=random.randint(max_speed_interval_truck[0],max_speed_interval_truck[1])
    elif veh_type=="bus":
        max_speed=random.randint(max_speed_interval_bus[0],max_speed_interval_bus[1])
    else:
        print("error of inputting vehicle type")                
    return max_speed 

def driver_ty_gen():
    random.seed(10)
    # this function randomly generate driver type, 0 or 1 (two types of drivers are optional)
    driver_type=random.randint(0,1)
    return driver_type 

def driver_value_time_gen(median_value_time):
    random.seed(10)
    # this function generates the value-of-time of the driver
    # a normal distribution is used to randomly generate the value-of-time for each driver
    mu=median_value_time
    sigma=mu/5.0    
    s = np.random.normal(mu, sigma, 1)    
    return s[0] 

def lane_change_p_gen(driver_type):
    random.seed(10)
    # this function generates the initial value of lane-change-ability for each driver
    # the probability is assumed to be related to the driver-type
    lane_change_p=0# initialize the lane-change-probability as 0 
    if driver_type==0:
        lane_change_p=random.randint(0,5)/10.0
    elif driver_type==1:
        lane_change_p=random.randint(6,10)/10.0
    else:
        print("input driver-type is error for generating lane-change-probability")
    return(lane_change_p)


def vehicle_gen(OD_matrix,gen_distribution,vehicle_id,dic_graph_low,median_value_time,dic_nodes,dic_vehicles,dic_time_vehids):
    # this function generates vehicles needed to be put into the road network based on the OD value
    # OD_value is a value of a OD pair in OD-matrix
    # gen_distribution is the distribution of vehicle generated and put onto the road network
    # the output is the dictionary of vehicles which will be used in the whole simulation period.
    # the key feature of a vehicle is the start time stamp
    
    if gen_distribution=="uniform":
        # the vehicles are evenly generated/put onto the network during the time slot
        # even generated in a uniform way, the start-time-stamp of vehicle has to be modified a bit to suit the convenience of time-step for simualtion
        
        for timeslot in OD_matrix.keys():
            for OD_label in OD_matrix[timeslot].keys():
                for vehicle_type in OD_matrix[timeslot][OD_label]:######******vehicle-type                    
                    OD_value=OD_matrix[timeslot][OD_label][vehicle_type]
                    start_timestamp,end_timestamp=obtain_time_stamp(timeslot)# two time stamps are in string type
                    #print start_timestamp,end_timestamp
                    #print type(start_timestamp),type(end_timestamp)
                    duration_timeslot=Caltime(start_timestamp,end_timestamp)# the duration of time slot of each csv file; unit in seconds
                    O,D=obtain_O_and_D(OD_label)######*******Origin and Destination
                    if OD_value>0:                
                        aver_interval=1.0*duration_timeslot/OD_value # the interval later will be modified to a up-close integer                       
                        for i in range(0,OD_value):# totally generate OD_value vehicles in this iteration
                            vehicle_start_timestamp=add_timestamp(start_timestamp,int(ceil(aver_interval*i)))######******* the time stamp when the vehicle is put on the network; in string type                                                                                                                                                             
                            ########*********obtain other features of this vehicle*********########
                            vehicle_id+=1
                            max_speed=vehicle_maxspeed(vehicle_type)
                            driver_type=driver_ty_gen()
                            value_time=driver_value_time_gen(median_value_time)
                            lane_change_p=lane_change_p_gen(driver_type)
                            ################  ATTENTION: the time-budget is obtained as the travel time calculated on the low-graph, if all vehicles are generated before putting them on the network,\
                            ################             it is the optimal one that is the free-flow travel time on the low-graph.
                            ################             Otherwise, if the vehicles are generated with time-steps in simulation, it is the real-time optimal travel time in which there are vehicles on the network.
                            dic_time_budgets,dic_best_route_nodes=shortestPathNode(dic_graph_low, O, D)  
                            dic_best_route_lanes=convert_ppath_to_pathids(dic_best_route_nodes,dic_graph_low,O,D)
                            next_nodeid=dic_best_route_nodes[O]    
                            #print time_budget
                            #print dic_graph_low.items()
                            #print O,D,best_route_initial    
                            #print type(O),type(D)
                            #print dic_nodes[O]
                            #print dic_nodes[D]                  
                            time_budget=ceil(dic_time_budgets[D])
                            vehicle_end_timestamp_expected=add_timestamp(vehicle_start_timestamp, time_budget)###########!!!make sure time-budget is in seconds
                            veh_list_timestamps=[vehicle_start_timestamp]
                            lane_id_initial=dic_graph_low[O][next_nodeid]['lane-id']
                            veh_dic_locations={vehicle_start_timestamp:{'coor-X':dic_nodes[O]['coor-X'],'coor-Y':dic_nodes[O]['coor-Y'],'lane-id':lane_id_initial}}
                            veh_dic_routes={vehicle_start_timestamp:dic_best_route_lanes}
                            
                            veh_lane_type=0
                            veh_lane_changed=[0,""]# dummy-of-change, and time stamp of changing lanes
                            veh_list_laneid_used=[lane_id_initial]
                            veh_endtime=''
                            speed=dic_graph_low[O][next_nodeid]['speed']
                            veh_dic_speeds={vehicle_start_timestamp:speed}
                            
                            vehicle=Vehicle(vehicle_id,max_speed,vehicle_type,driver_type,value_time,lane_change_p,O,D,time_budget,vehicle_start_timestamp, \
                                            vehicle_end_timestamp_expected,veh_list_timestamps, veh_dic_locations,veh_dic_routes, \
                                            veh_lane_type,veh_lane_changed,veh_list_laneid_used,veh_endtime,veh_dic_speeds)                            
                            dic_vehicles,dic_time_vehids=read_vehicle(vehicle,dic_vehicles,dic_time_vehids)      
                              
    else:
        print("wrong input for vehicle-generation distribution")    
    
    return dic_vehicles,dic_time_vehids

'''
# set/calculate the median of value-of-time used in the study
median_value_time=50# the median of value-of-time in SG, used to the check the person  
# initialize vehicle-id; it is a global variable, as there may be many OD-matrix
vehicle_id=0# the first vehicle id is 1 and is increased subsequently with a step of 1
# initialize the time-step used for update during the simulation
time_step=1# unit in sec
dic_vehicles={}# initialize the dictionary of vehicles
dic_time_vehids={}
##############################################################################################################
# as the vehicle objects need the initialized network information, the geometry needs to be read, too.
from a_ReadRoadNetwork.readgeometry import *
dic_graph_high={}
dic_graph_low={}
dic_lanes={}
dic_nodes={}
# import csv files where the node and lane data are stored
infile_node=open(r"D:\03Work during PD\31ERP2_in_COI\Sioux Falls network\nodes-SiouxFalls_gong.csv","r")
infile_node.readline()# jump the first row of column head
infile_lane=open(r"D:\03Work during PD\31ERP2_in_COI\Sioux Falls network\lanes-SiouxFalls_gong.csv","r")
infile_lane.readline()# jump the first row of column head

dic_nodes=ReadNodes(infile_node,dic_nodes)
dic_graph_high,dic_graph_low,dic_lanes=ReadLanes(infile_lane)

# calculate the length of lanes
dic_graph_low =LengthCal(dic_graph_low, dic_nodes)
dic_graph_high=LengthCal(dic_graph_high,dic_nodes)
dic_lanes=LengthCal2(dic_lanes)
print "        "
print "the items of lanes are printed as follows"
for key in dic_lanes:
    print dic_lanes[key]

print "        "
#############################################################################################################
#update the file path of folder containing the OD matrices as below
folderpath=r"D:\03Work during PD\31ERP2_in_COI\meso_by_python\OD_data"

OD_matrices=ReadOD(folderpath)
dic_vehicles,dic_time_vehids=vehicle_gen(OD_matrices, 'uniform',vehicle_id,dic_graph_low,median_value_time,dic_nodes,dic_vehicles,dic_time_vehids)
print len(dic_vehicles)


for key in dic_vehicles:
    print key,dic_vehicles[key]
'''