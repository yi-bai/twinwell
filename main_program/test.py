'''
Created on 2018/07/24

@author: gong

This is a test function for checking the function named as convert_ppath_to_pathids

'''
a={}
for i in range(0,10):
    a[i]=i

for item in a:
    print item


for item in a:
    print item
    
    
for j in range(5,8):
    if a.has_key(j):
        print "a has this key", j
        
        
def add_value():
    for k in range (100,105):
        a[k]=k

add_value()
print " this is the added a"
for item in a:
    print item,a[item]
    