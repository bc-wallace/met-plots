
# coding: utf-8

# In[1]:

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import matplotlib
from datetime import datetime, timedelta
from mpl_toolkits.basemap import Basemap


# In[2]:

#enter various info
#use a for loop if you want to use multiple stations
days=5
day1='10'
day2='15'
station='KMLB'
startdate='20160510'


# In[3]:

#converts nonreadable data into nan
def s2f(csv_file):
        return [float('NaN') if 'M' in x else float(x) for x in csv_file]

#startdate MUST be in YYYYMMDD!
#this time creates a uniform 1 minute array across a specified length of time
#useful for plotting
def etime(startdate,days):
    date=datetime.strptime(startdate,'%Y%m%d')
    str_time=np.zeros(1440*days)
    for x in range(len(str_time)):
        minute='0'+str(date.minute) if date.minute<10 else str(date.minute)
        hour='0'+str(date.hour) if date.hour<10 else str(date.hour)
        day=str(date.day)
        str_time[x]=day+hour+minute
        date+=timedelta(minutes=1)
    return str_time


# In[4]:

path_6406='ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/6406-2016/64060'+station+'201605.dat'

#this path leads to other data like humidity etc
#path_6405='ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/6405-2016/64050KVRB201605.dat'


# In[5]:

#assign random placeholder for name 
file_6406=pd.read_csv(path_6406,names='t')


# In[6]:

station=file_6406['t'][0][5:9]
day=[]
time=[]
pres1=[]
pres2=[]
pres3=[]
tmpf=[]
dwpf=[]


# In[7]:

#pull in character position of relevant data
#crude workaround the inconsistent nature of the data 
for row in enumerate(file_6406['t']):
    x=row[0]
    day.append(file_6406['t'][x][19:21])
    time.append(file_6406['t'][x][21:25])

    pres1.append(file_6406['t'][x][70:76])
    pres2.append(file_6406['t'][x][78:84])
    pres3.append(file_6406['t'][x][86:92])

    tmpf.append(file_6406['t'][x][95:97])
    dwpf.append(file_6406['t'][x][100:102])


# In[8]:

#finding endpoints within data that correspond to start day and stop day
#recommended that day1 and day2 be different days
for val in enumerate(day):
    if val[1]==day1:
        st=val[0]
        break
for val in enumerate(day):
    if val[1]==day2:
        en=val[0]
        break


# In[9]:

day=s2f(np.array(day[st:en]))
time=np.array(time[st:en])
pres1=np.array(s2f(pres1[st:en]))
pres2=np.array(s2f(pres2[st:en]))
pres3=np.array(s2f(pres3[st:en]))
tmpf=np.array(s2f(tmpf[st:en]))
dwpf=np.array(s2f(dwpf[st:en]))


# In[10]:

#averaging the 3 pressure readings and converting to hPa
#why is this in inches to begin with?
pres=((pres1+pres2+pres3)/3)*33.8639


# In[11]:

full_time=etime(startdate,days)


# In[12]:

y=0

mpres=np.zeros(len(full_time))
mtmpf=np.zeros(len(full_time))
mdwpf=np.zeros(len(full_time))

for x in range(len(full_time)):
    if y>1:
        if time[y]==time[y-1]:
            #print 'Discontinuity Error! \n Fixing.....'
            y+=1
    if str(int(full_time[x]))==str(int(day[y]))+time[y]:
        mpres[x]=pres[y]
        mtmpf[x]=tmpf[y]
        mdwpf[x]=dwpf[y]
        y+=1
        #print 'Equal!'
    else:
        mpres[x]=float('NaN')
        mtmpf[x]=float('NaN')
        mdwpf[x]=float('NaN')
        #print 'Not Equal!'


# In[13]:

fig,ax=plt.subplots(2,1)
fig.set_figheight(12)
fig.set_figwidth(14)
array_pos=0
start_day=[0,]
end_day=[]

tick_interval=4*days
base=len(full_time)/tick_interval
if base==0:
    print 'Not enough times'
labels=full_time[0::base]
labels=np.insert(labels,0,0)
loc=plticker.MultipleLocator(base=base)
y_formatter=matplotlib.ticker.ScalarFormatter(useOffset=False)

for x in range(1,len(full_time)):
    if str(full_time[x])[:2] > str(full_time[x-1])[:2]:
        end_day.append(array_pos)
        start_day.append(array_pos+1)
    array_pos+=1
end_day.append(len(full_time))

ax[0].plot(np.arange(0,len(full_time),1),mtmpf,'b',linewidth=2)
ax[0].plot(np.arange(0,len(full_time),1),mdwpf,'r',linewidth=2)
for i in range(0,len(start_day),2):
    ax[0].axvspan(start_day[i],end_day[i],color='#CECECE')
ax[0].set_xlim(0,len(full_time)-1)
ax[0].set_xticklabels([])
ax[0].grid()

ax[1].plot(np.arange(0,len(full_time),1),mpres,'k',linewidth=2)
for i in range(0,len(start_day),2):
    ax[1].axvspan(start_day[i],end_day[i],color='#CECECE')
ax[1].set_xlim(0,len(full_time)-1)
#changes yaxis values to be full integers
ax[1]= plt.gca()
ax[1].ticklabel_format(useOffset=False)
#sets xaxis labels to be normal
ax[1].xaxis.set_major_locator(loc)
ax[1].set_xticklabels(labels,rotation='90')

ax[1].set_xlim(0,len(full_time)-1)
ax[1].grid()

plt.show()
plt.close()


# In[ ]:


