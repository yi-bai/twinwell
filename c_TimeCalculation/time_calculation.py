'''
Created on 2018/08/03

@author: gong

This module contains the time related functions used in the simulator.
The input and output time-stamps are all string type; the input stamps are converted to datetime type firstly.
the output stamps are converted to string types before returned.
'''
import time,datetime


def get_pre_timestamp(cur_time,timestep):
    # this function returns the previous time stamp which is "timestep" less than current time stamp
    # cur_time is the current time stamp, string type
    cur_time=datetime.datetime.strptime(cur_time,"%Y-%m-%d %H:%M:%S")# change the type to datetime from string    
    timestep=float(timestep)    
    timestep=datetime.timedelta(seconds=timestep)
    pre_timestamp=cur_time-timestep
    pre_timestamp=str(pre_timestamp)[:19]
    return pre_timestamp# output is string type in format of yyyy-mm-dd hh:mm:ss
def get_nex_timestamp(cur_time,timestep):
    # this function returns the next time stamp which is "timestep" more than current time stamp
    # cur_time is the current time stamp, string type
    cur_time=datetime.datetime.strptime(cur_time,"%Y-%m-%d %H:%M:%S")# change the type to datetime from string    
    timestep=float(timestep)    
    timestep=datetime.timedelta(seconds=timestep)
    nex_timestamp=cur_time+timestep
    nex_timestamp=str(nex_timestamp)[:19]
    return nex_timestamp# output is string type in format of yyyy-mm-dd hh:mm:ss
def Caltime(date1,date2): #This function used to calculate time difference between two time stamp, and result are in seconds
    # input date should be string type
    date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
    date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
    return ((date2-date1).days*86400+(date2-date1).seconds)# in seconds
def add_timestamp(cur_time,timestep):
    # this function returns the a new time stamp which is "timestep" more than current time stamp
    # cur_time is the current time stamp, in the format of yyyy-mm-dd hh:mm:ss
    # timestep is in seconds
    # the returned output is also in the format of 'yyyy-mm-dd hh:mm:ss' in the string type
    cur_time=datetime.datetime.strptime(cur_time,"%Y-%m-%d %H:%M:%S")
    timestep=float(timestep)
    timestep=datetime.timedelta(seconds=timestep)
    new_timestamp=cur_time+timestep
    new_timestamp=str(new_timestamp)[:19]
    return new_timestamp# the output is string type

'''
# set the default of time step
timestep=1# unit is seconds

nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print nowtime,type(nowtime)
print 'now change to datetime type'
nowtime=datetime.datetime.strptime(nowtime,'%Y-%m-%d %H:%M:%S')
print nowtime,type(nowtime)
date2="2018-08-07 11:31:40"
print date2[:19]

#print Caltime(nowtime, date2),"OK,checked"
print add_timestamp(str(nowtime), timestep)
'''
