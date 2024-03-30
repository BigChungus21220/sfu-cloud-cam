# runs all the analysis on the data

import matplotlib.pyplot as plt
import os
import time
from datetime import datetime as dt
from datetime import timedelta

daylight_savings_begin = dt.strptime("Mar 10, 2024", '%b %d, %Y')

#for all cameras
#   for all days
#       load data file
#       for each timestamp
#           enumerate data
#           push data to day
#       push data to camera for day
#

def timeToKey(time):
    # parse hour + minute
    hour = int(time[0:2])
    minute = int(time[3:5])
    # run calculation
    return hour*60 + minute - 60

def minutes_to_datetime(minutes_since_midnight):
    hours = minutes_since_midnight // 60
    minutes = minutes_since_midnight % 60
    
    time_delta = timedelta(hours=hours, minutes=minutes)
    current_date = dt.now().date()
    result_datetime = dt.combine(current_date, dt.min.time()) + time_delta
    
    return result_datetime


# load all the data from one file
def load_data(filepath):
    dataout = {}
    f = open(filepath, "r")
    while f:
        line = f.readline()
        if line == "":
            break
        dataout[timeToKey(line[0:5])] = float(line[6:-1])
    f.close()
    return dataout

# interpolate any gaps from 5-15 minutes long
# if not on a 5 min time, interpolate to round
def fill_gaps(datain):
    dataout = {}
    for i in range(timeToKey("01:00"),timeToKey("24:55"),5):
        # if datapoint exists, then push it
        if i in datain:
            dataout[i] = datain[i]
        else: # need to interpolate
            a = 0
            b = 0
            for key in datain:
                b = key
                if key > i: break
                a = b
            
            if b-a <= 15 and a != b: # discard point if there is a hole in the data that's too big
                dataout[i] = datain[a]*(1-(i-a)/(b-a)) + datain[b]*(i-a)/(b-a)
    return dataout

# get the average value from 7am-4pm for a camera for a day
def daily_average(data):
    sum = 0
    denom = 0
    for i in range(timeToKey("07:00"),timeToKey("16:00"),5):
        if i in data:
            sum += data[i]
            denom += 1
    # take average
    return sum/denom

# get the average for a certain time of day over the whole recording period
def time_average(data, key):
    sum = 0
    denom = 0
    for day in data:
        if key in day:
            sum += day[key]
            denom += 1
    if denom == 0: return 0
    return sum/denom

class cameraSetting:
    def __init__(self, path, color, name):
        self.path = path
        self.color = color
        self.name = name
    

cameras = []
settings = [
    cameraSetting("./output/libWest/", "red", "Library West"),
    cameraSetting("./output/towNorth/", "green", "Tower Road North"),
    cameraSetting("./output/towSouth/", "blue", "Tower Road South"),
    cameraSetting("./output/aqSouthEast/", "purple", "Academic Quadrangle Southeast"),
    cameraSetting("./output/apiOutput/", "black", "Weather API Output")
]

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)

fig3 = plt.figure()
ax3 = fig3.add_subplot(111)

i = 0
for setting in settings:
    #figk = plt.figure()
    #axk = figk.add_subplot(111)
    
    cameras.append([])
    directory = os.fsencode(setting.path)

    # get data
    days = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        filedate = dt.strptime(filename[0:10], '%Y-%m-%d') #find way to store with data
        days.append(filedate)
        cameras[-1].append(load_data(setting.path + filename))
    
    # clean up data
    for data in cameras[-1]:
        data = fill_gaps(data)
    
    # get time avgs
    time_avgs = []
    times = []
    for time in range(timeToKey("01:00"),timeToKey("24:55"),5):
        time_avgs.append(time_average(cameras[-1],time))
        times.append(minutes_to_datetime(time))
        
    # get sample day
    test_y = []
    test_x = []
    for key in cameras[-1][21]:
        test_y.append(cameras[-1][21][key])
        test_x.append(minutes_to_datetime(key))
    
    # get day avgs
    day_avgs = []
    j = 0
    for data in cameras[-1]:
        data = fill_gaps(data)
        day_avgs.append(daily_average(data))
        #axk.scatter(data.keys(),data.values(),color=(j/len(cameras[-1]),0,1-j/len(cameras[-1]),0.7))
        j += 1
    #figk.show()

    ax1.plot(days, day_avgs, label=setting.name, color=setting.color)
    ax2.plot(times, time_avgs, label=setting.name, color=setting.color)
    ax3.plot(test_x, test_y, label=setting.name, color=setting.color)
    i += 1
# draw plots
ax1.set_xlabel('Day')
ax1.set_ylabel('Cloud Coverage')
ax1.set_title('Average Daily Cloud Coverage on Burnaby Mountain from Feb 25 to Mar 23, 2024')
ax1.legend(loc='lower right')

ax2.set_xlabel('Time')
ax2.set_ylabel('Cloud Coverage')
ax2.set_title('Average Time Cloud Coverage on Burnaby Mountain from Feb 25 to Mar 23, 2024')
ax2.legend(loc='lower right')

ax3.set_xlabel('Time')
ax3.set_ylabel('Cloud Coverage')
ax3.set_title('Cloud Coverage on Burnaby Mountain on Mar 17, 2024')
ax3.legend(loc='lower right')

plt.tight_layout()

plt.show()
