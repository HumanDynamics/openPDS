__author__ = 'jbt'
import time
import math
#import pdb


newmotiondata = []

def update(x, y, z, count, variancesum, avg, sums):
    count+=1
    magnitude = math.sqrt(x**2+y**2+z**2)
    newavg = (count-1)*avg/count + magnitude/count
    deltaavg = newavg - avg
    variancesum += (magnitude-newavg)*(magnitude-newavg) - 2*(sums-(count-1)*avg) + (count-1)*(deltaavg*deltaavg)
    sums += magnitude
    avg = newavg
    return (variancesum, sums, avg)


def intervalreset(timestamp, high, low, variancesum):
    #insert high low data, then reset
    #calculate activity and reset

    if variancesum >=10:
        high +=1
    elif variancesum<10 and variancesum>3:
        low +=1

    ActivityProbe ={
     "edu.mit.media.funf.probe.builtin.ActivityProbe": {
    "_id": {
      "$oid": "540a2b2491cfc86cda60813c"
    },
    "key": "edu.mit.media.funf.probe.builtin.ActivityProbe",
    "time": timestamp,
    "value": {
      "high_activity_intervals": high,
      "low_activity_intervals": low,
      "timestamp": timestamp,
      "total_intervals": high+low
    }
    }
    }

    newmotiondata.append(ActivityProbe)



def ondatareceived(motiondata):
    count = 1
    variancesum = 0
    avg = 0
    sums = 0
    interval = 1
    starttime = 0
    lowactintcount = 0
    highactintcount = 0
    intervalstarttime = 0

    for data in motiondata:
        pdb.set_trace()
        try:
            timestamp = int(time.mktime(time.strptime(data['datetime'], '%Y-%m-%d %H:%M'))) - time.timezone
            intervalstarttime = int(time.mktime(time.strptime(data['datetime'], '%Y-%m-%d %H:%M'))) - time.timezone
        except ValueError as e:
            timestamp = int(time.mktime(time.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S'))) - time.timezone
            intervalstarttime = int(time.mktime(time.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S'))) - time.timezone
        except ValueError as e:
            timestamp = int(time.mktime(time.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S:%f'))) - time.timezone
            intervalstarttime = int(time.mktime(time.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S:%f'))) - time.timezone
        else:
            print "datetime could not be parsed"
            print data['datetime']

        if timestamp >= intervalstarttime + 2* interval:
            # reset the timestamp
            variancesum = avg = sums = count = 0
            starttime = intervalstarttime = timestamp
            variancesum = avg = count = 0
            intervalcount = 0
            lowactintcount = 0
            highactintcount = 0

        else:

            intervalreset(timestamp, highactintcount, lowactintcount, variancesum)

        x = data['rotationRate_x']
        y = data['rotationRate_y']
        z = data['rotationRate_z']
        (variancesum, sums, avg) = update(x, y, z, count, variancesum, avg, sums)

        lowactintcount +=1
        highactintcount+=1
    return newmotiondata

