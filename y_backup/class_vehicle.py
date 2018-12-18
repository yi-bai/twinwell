'''
Created on 2018/07/04

This module is generate the different types of vehicles with their profiles.
Currently, three types of vehicle can be included, which are car, bus and truck
The profiles of vehicle include max speed, lane-changing probability, time value so far. 

max speed is constant for each type of vehicle, car 60km/h, bus 40km/h, truck 50km/h.
The value of time is set according the average wage per hour online(https://www.payscale.com/research/SG/Location=Singapore/Hourly_Rate) which is from 7 to 41 SD
Lane-changing probability is set as that the driver whose value of time is more than the middle value in the above is definitely to change for a faster lane when the estimated travel time is more than expected.


@author: gong
'''
   
class Vehicle(object):
    def __init__(self,vehicle_id,max_speed,veh_type,driver_type,value_time,lane_chan_probability,origin,destination,time_budget,vehicle_start_timestamp,vehicle_end_timestamp_expected,veh_list_timestamp,veh_dic_locations,veh_dic_routes):
        self.vehicleid=vehicle_id
        self.veh_type=veh_type#vehicle type
        self.max_speed=max_speed#the max speed of this type of vehicle can achieve
        self.driver_type=driver_type#driver type, not applicable to bus driver
        self.value_time=value_time#value of time of the driver, not applicable to bus driver
        self.lane_chan_probability=lane_chan_probability#the probability of changing lane
        self.origin=origin# a node's id; has same features as a node
        self.destination=destination# a node's id; has same features as a node
        self.time_budget=time_budget
        self.starttime=vehicle_start_timestamp# time to put the vehicle into the road network
        self.expected_endtime=vehicle_end_timestamp_expected# expected end time decided by the start time and the time budget
        # features below are initialized as blank and no need to be imported from outside  
        self.list_timestamp=veh_list_timestamp# 'yyyy-mm-dd hh:mm:ss', store the time stamps from when the vehicle is generated to when it reaches its destinations. A simulation step is the difference between each pair of consecutive time stamps.
        self.dic_locations=veh_dic_locations# store the locations of vehicle at each time stamp; key is the time stamp and the value is another dictionary {corr-X:corr-X,corr-Y,corr-Y,lane-id:lane-id] of corresponding location.
        self.dic_routes=veh_dic_routes# store the best path at current time stamp; key is the time stamp and the value is a dictionary which similar to P of function Dijkstra, {lane1:lane3,lane3:lane2,lane2:lane22,lane22:lane43,...}

# initialize the dictionary of vehicles
dic_vehicles={}# all vehicles; key is the vehicle id and a dictionary containing other features is used as the value. {vehid1:{'veh-type':veh_type,'max-speed':max_speed,....},vehid2:{... ...},vehid3:....} 
# read vehicle one by one and included in the dictionary of vehicles
def read_vehicle(vehicle,dic_vehicles):
    #this function read the features of an object vehicle into the dictionary of vehicles, whose key is the feature name and the value is corresponding to the feature-name
    if dic_vehicles.has_key(vehicle.vehicleid):
        print("duplicate vehicle IDs, sth wrong")
    else:
        dic_vehicles[str(vehicle.vehicleid)]={'vehicle-id':vehicle.vehicleid,'veh-type':vehicle.veh_type,'max-speed':vehicle.max_speed,'driver-type':vehicle.driver_type, \
                                              'value-time':vehicle.value_time,'lane-chan-p':vehicle.lane_chan_probability,'origin':vehicle.origin,'destination':vehicle.destination, \
                                              'time-buget':vehicle.time_budget,'start-timestamp':vehicle.starttime,'expected-endtime':vehicle.expected_endtime, \
                                              'list-timestamps':vehicle.list_timestamp,'dic-locations':vehicle.dic_locations,'dic-routes':vehicle.dic_routes}       
    return()


           
            
        
        