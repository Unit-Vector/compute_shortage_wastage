
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import pdb


# In[8]:


data=pd.read_csv('/Users/yuemeimei/Desktop/car_evaluation.csv',encoding="utf-8")


# In[12]:


data=data['buying,maint,doors,persons,lug_boot,safety,condition'].str.split(r',',expand=True)


# In[20]:


data=data.rename(columns={0:"buying",1:"maint",2:'doors',3:'persons',4:'lug_boot',5:'safety',6:'condition'})


# In[21]:


data.to_csv('car_condition.csv',index=False)


# In[50]:


unit=3
#forecast_us =[0,0,0,1,1,0,1,0,2,2,1,2,2,2,4,6,6,1,10,8,2]  #预估量
actual_us = [0,0,0,1,1,0,0,1,0,3,3,3,3,2,5,4,2,3,8,5,4] #实际售卖量
storage_time = [5]*len(forecast_us)
produce_time = [1, 0, 0]*int(len(forecast_us)/3)
valid_time = 4
cost_time = 1 #制作时间


# In[51]:


def update_status(tot_data, valid_time, time, cost_time, produce_time):
    #库存量=制作+库存-售卖-损耗
    this_storage = tot_data.loc[time,'produce_end'] + tot_data.loc[time-1,'storage'] - tot_data.loc[time-1,'sold'] - tot_data.loc[time-1,'wastage']
    tot_data.loc[time, 'batch'] = tot_data.loc[time,'batch'] + tot_data.loc[time,'produce_end']
    tot_data.loc[time, 'storage'] = this_storage
    
    #制作量=需存量-库存
    if produce_time[time]>0:
        this_produce = max(tot_data.loc[time, 'min_storage'] - this_storage, 0) 
        tot_data.loc[time,'produce'] = this_produce
        tot_data.loc[time+cost_time,'produce_end'] = this_produce
    
    #缺货量
    this_sell = tot_data.loc[time,'sold']
    
    if this_sell-this_storage>0:
        tot_data.loc[time,'shortage'] = this_sell - this_storage
    
    #损耗
    #pdb.set_trace()
    while this_sell>0:
        ind = np.where(tot_data['batch']>0)[0]
        if len(ind)==0:
            ind = np.where((tot_data.loc[(time+1):,'produce_end']>0) & 
                           (tot_data.loc[(time+1):,'produce_end']+tot_data.loc[(time+1):,'batch']>0))[0]
            if len(ind)==0:
                ind = np.where(produce_time[time:]>0)[0]
                if len(ind)>0:
                    ind = min(ind) + cost_time + time
                    if (ind<tot_data.shape[0]):
                        tot_data.loc[ind,'batch'] = tot_data.loc[ind,'batch'] - this_sell
                    else:
                        tot_data.loc[len(produce_time)-1,'batch'] = tot_data.loc[len(produce_time)-1,'batch'] - this_sell
                else:
                    tot_data.loc[len(produce_time)-1,'batch'] = tot_data.loc[len(produce_time)-1,'batch'] - this_sell
                this_sell = 0
            else:
                ind = min(ind) + time + 1
                minus = min(tot_data.loc[ind,'produce_end'], this_sell)
                tot_data.loc[ind,'batch'] = tot_data.loc[ind,'batch'] - minus
                this_sell = this_sell - minus
        else:
            ind = min(ind)
            minus = min(tot_data.loc[ind,'batch'],this_sell)
            tot_data.loc[ind,'batch'] = tot_data.loc[ind,'batch'] - minus
            this_sell = this_sell - minus
    
    if time>=valid_time:
        if tot_data.loc[time+1-valid_time,'batch']>0:
            tot_data.loc[time,'wastage'] = tot_data.loc[time+1-valid_time,'batch']
            tot_data.loc[time+1-valid_time,'batch'] = 0
    
    return     


# In[52]:


storage = np.array([0]*len(forecast_us))
#min_storage = [sum(forecast_us[time:(time+storage_time[time])]) for time in range(len(forecast_us))]  #需存量
min_storage=[2,0,0,3,0,0,6,0,0,9,0,0,20,0,0,31,0,0,20,0,0]
produce = np.array([0]*len(forecast_us))
produce_end = np.array([0]*len(forecast_us))
sold = np.array(actual_us)  #实际售卖量
wastage = np.array([0]*len(forecast_us))
shortage = np.array([0]*len(forecast_us))
batch = np.array([0]*len(forecast_us))
produce[0] = min_storage[0]
produce_end[cost_time] = min_storage[0]
produce_time = np.array(produce_time)
tot_data = pd.DataFrame({'min_storage':min_storage,
                         'storage':storage,
                         'produce':produce,
                         'produce_end':produce_end,
                         'batch':batch,
                         'sold':sold,
                         'wastage':wastage,
                        'shortage':shortage})



# In[54]:


for time in range(1,15):
    update_status(tot_data, valid_time, time, cost_time, produce_time)
print(tot_data.sum(axis=0))

tot_data


# In[48]:


tot_data.T

