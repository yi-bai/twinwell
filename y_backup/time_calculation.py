'''
Created on 2018/08/03

@author: gong
'''
import time,datetime

# set the default of time step
timestep=1# unit is seconds
def get_pre_timestamp(cur_time,timestep):
    # this function returns the previous time stamp which is "timestep" less than current time stamp
    # cur_time is the current time stamp, in the format of hh:mm:ss
    today=datetime.datetime.now().date()# date of today, used to combine with current time to make a complete combination of date and time
    cur_time=str(today)+" "+str(cur_time)# date + time
    cur_time=datetime.datetime.strptime(cur_time,"%Y-%m-%d %H:%M:%S")# change the type to datetime from string    
    timestep=float(timestep)    
    timestep=datetime.timedelta(seconds=timestep)
    pre_timestamp=cur_time-timestep
    pre_timestamp=str(pre_timestamp)
    return pre_timestamp
def get_nex_timestamp(cur_time,timestep):
    # this function returns the next time stamp which is "timestep" more than current time stamp
    # cur_time is the current time stamp, in the format of hh:mm:ss
    today=datetime.datetime.now().date()# date of today, used to combine with current time to make a complete combination of date and time
    cur_time=str(today)+" "+str(cur_time)# date + time
    cur_time=datetime.datetime.strptime(cur_time,"%Y-%m-%d %H:%M:%S")# change the type to datetime from string    
    timestep=float(timestep)    
    timestep=datetime.timedelta(seconds=timestep)
    nex_timestamp=cur_time+timestep
    nex_timestamp=str(nex_timestamp)
    return nex_timestamp
def Caltime(date1,date2): #This function used to calculate time difference between two time stamp, and result are in seconds
    # input date should be string type
    date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
    date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
    return ((date2-date1).days*86400+(date2-date1).seconds)