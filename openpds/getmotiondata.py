__author__ = 'jbt'
import time
import math
import pdb


newmotiondata = [{
     "edu.mit.media.funf.probe.builtin.ActivityProbe": {
    "_id": {
      "$oid": "540a2b2491cfc86cda60813c"
    },
    "key": "edu.mit.media.funf.probe.builtin.ActivityProbe",
    "time": 0,
    "value": {
      "high_activity_intervals": 0,
      "low_activity_intervals": 0,
      "timestamp": 0,
      "total_intervals": 0
    }
    }
    }]

def update(x, y, z, count, variancesum, avg, sums):
    count+=1
    magnitude = math.sqrt(x**2+y**2+z**2)
    newavg = (count-1)*avg/count + magnitude/count
    deltaavg = newavg - avg
    variancesum += (magnitude-newavg)*(magnitude-newavg) - 2*(sums-(count-1)*avg) + (count-1)*(deltaavg*deltaavg)
    sums += magnitude
    avg = newavg
    return (variancesum, sum, avg)


def reset(timestamp):

    #if more than an interval away, start a new scan
    variancesum = avg = sums = count = 0
    starttime = intervalstarttime = timestamp
    variancesum = avg = count = 0
    intervalcount = 0
    lowactintcount = 0
    highactintcount = 0

def intervalreset(timestamp, high, low, variancesum):
    #insert high low data, then reset
    #calculate activity and reset
    pdb.set_trace()
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
    pdb.set_trace()
    for data in motiondata:
        timestamp = int(time.mktime(time.strptime(data['datetime'], '%Y-%m-%d %H:%M'))) - time.timezone
        intervalstarttime = int(time.mktime(time.strptime(data['datetime'], '%Y-%m-%d %H:%M'))) - time.timezone
        if timestamp >= intervalstarttime + 2* interval:
            reset(timestamp)
        elif (timestamp >= intervalstarttime + interval):
            intervalreset(timestamp, highactintcount, lowactintcount, variancesum)

        x = data['rotationRate_x']
        y = data['rotationRate_y']
        z = data['rotationRate_z']
        (variancesum, sums, avg) = update(x, y, z, count, variancesum, avg, sums)

    return newmotiondata

a= [{
    "rotationRate_z": 0.1928441524505615,
    "gravity_y": -0.7093989253044128,
    "userAcceleration_x": -0.09338897466659546,
    "attitude_pitch": 0.7886450220020825,
    "rotationRate_x": 0.2315706014633179,
    "userAcceleration_z": -0.09338897466659546,
    "attitude_yaw": -0.07383178064774487,
    "gravity_z": -0.6854852437973022,
    "rotationRate_y": -0.1779242157936096,
    "probe": "motion",
    "attitude_x": 0.2346942677939474,
    "gravity_x": 0.163899838924408,
    "userAcceleration_y": -0.09338897466659546,
    "datetime": "2014-09-25 13:33"
}, {
    "rotationRate_z": 0.1898728609085083,
    "gravity_y": -0.7162162065505981,
    "userAcceleration_x": -0.07178672403097153,
    "attitude_pitch": 0.7983652636390012,
    "rotationRate_x": 0.2851479351520538,
    "userAcceleration_z": -0.07178672403097153,
    "attitude_yaw": -0.06403246739085629,
    "gravity_z": -0.6813748478889465,
    "rotationRate_y": -0.2980103492736816,
    "probe": "motion",
    "attitude_x": 0.2179085556574697,
    "gravity_x": 0.1508730351924896,
    "userAcceleration_y": -0.07178672403097153,
    "datetime": "2014-09-25 13:33"
}, {
    "rotationRate_z": 0.1906691193580627,
    "gravity_y": -0.7217040657997131,
    "userAcceleration_x": -0.06914905458688736,
    "attitude_pitch": 0.8062610118918628,
    "rotationRate_x": 0.337273508310318,
    "userAcceleration_z": -0.06914905458688736,
    "attitude_yaw": -0.06060854344104605,
    "gravity_z": -0.6771725416183472,
    "rotationRate_y": -0.2908459007740021,
    "probe": "motion",
    "attitude_x": 0.2087639023267831,
    "gravity_x": 0.1434593498706818,
    "userAcceleration_y": -0.06914905458688736,
    "datetime": "2014-09-25 13:35"
}, {
    "rotationRate_z": 0.2329283952713013,
    "gravity_y": -0.7278443574905396,
    "userAcceleration_x": -0.06540850549936295,
    "attitude_pitch": 0.8151731409532149,
    "rotationRate_x": 0.36366006731987,
    "userAcceleration_z": -0.06540850549936295,
    "attitude_yaw": -0.0497328105657588,
    "gravity_z": -0.673439621925354,
    "rotationRate_y": -0.3348692953586578,
    "probe": "motion",
    "attitude_x": 0.1897085974347726,
    "gravity_x": 0.1293123066425323,
    "userAcceleration_y": -0.06540850549936295,
    "datetime": "2014-09-25 13:33"
}]

print ondatareceived(a)