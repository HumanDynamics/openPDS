import pprint
from celery import task
import time
from datetime import date, timedelta
from collections import Counter
from oms_pds.internal.mongo import getInternalDataStore
from oms_pds.pds.models import Profile

def getStartTime(daysAgo, startAtMidnight):
    currentTime = time.time()
    return int(time.mktime((date.fromtimestamp(currentTime) - timedelta(days=daysAgo)).timetuple()) if startAtMidnight else currentTime - daysAgo * 24 * 3600)

def timeToBlock(t, numBlocks, blockLength):
    secondsIntoDay = int(t - time.mktime(date.fromtimestamp(t).timetuple()))
    return secondsIntoDay / blockLength

def stringKeys(d):
    if isinstance(d, dict):
        r = {}
        for k in d:
            r[str(k)] = stringKeys(d[k])
        return r
    elif isinstance(d, list) or isinstance(d, set):
        r = [stringKeys(el) for el in d]
        return r
    else: 
        return d            

@task()
def computeFingerprint(ids):
    numBlocks = 4
    blockLength = (24 / numBlocks) * 3600
    blockOverlap = 1800
    baselineStart = getStartTime(14, True)
    # To simplify things, make baselineStart on a Monday
    baselineStart = baselineStart - date.fromtimestamp(baselineStart).weekday() * 24 * 3600
    start = getStartTime(1, False)
    baselineAPs = ids.getData("WifiProbe", baselineStart, start) or []
    baselineAPs = [(ap["time"], ap["value"]["bssid"]) for ap in baselineAPs]
    baselineAPsByBlock = { day: { block: [] for block in range(0, numBlocks) } for day in range(0,7) }

    for ap in baselineAPs:
        baselineAPsByBlock[date.fromtimestamp(ap[0]).weekday()][timeToBlock(ap[0], numBlocks, blockLength)].append(ap[1])

    baselineAPsByBlock = { day: { block: [ap[0] for ap in Counter(baselineAPsByBlock[day][block]).most_common(10)] for block in range(0, numBlocks)} for day in range(0, 7)}
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(baselineAPsByBlock)
    testAPs = ids.getData("WifiProbe", start, None)
    testAPs = [(ap["time"], ap["value"]["bssid"]) for ap in testAPs]
    testAPsByBlock = {}
    for ap in testAPs:
        weekday = date.fromtimestamp(ap[0]).weekday()
        block = timeToBlock(ap[0], numBlocks, blockLength)
        if weekday not in testAPsByBlock:
            testAPsByBlock[weekday] = { block: [ap[1]] }
        elif block not in testAPsByBlock[weekday]:
            testAPsByBlock[weekday][block] = [ap[1]]
        else:
            testAPsByBlock[weekday][block].append(ap[1])
    
    testAPsByBlock = { day: { block: [ap[0] for ap in Counter(testAPsByBlock[day][block]).most_common(10)] for block in testAPsByBlock[day]} for day in testAPsByBlock}
    
    baseline= {}
    similarity = {}
    for day in testAPsByBlock:
        baseline[day] = {}
        similarity[day] = {}
        for block in testAPsByBlock[day]:
            print "Day: %s, Block %s"%(day, block)
            base = set(baselineAPsByBlock[day][block])
            test = set(testAPsByBlock[day][block])
            baseline[day][block] = base
            pp.pprint(base)
            pp.pprint(test)
            overlap = len(base.union(test))
            jaccard = float(len(base.intersection(test))) / overlap if overlap > 0 else 0
            similarity[day][block] = jaccard
            print "Jaccard: %s"%jaccard

    ids.saveAnswer("AuthFingerprint", { "base": stringKeys(baseline), "test": stringKeys(testAPsByBlock), "similarity": stringKeys(similarity)})

def computeAllFingerprints():
    for profile in Profile.objects.all():
        print profile.uuid
        ids = getInternalDataStore(profile, "Living Lab", "Auth", "")
        computeFingerprint(ids)
    
def getTopAccessPointsForTimeRange(ids, start, end, num = 5):
    accessPoints = ids.getData("WifiProbe", start, end)
    if accessPoints.count() > 0:
        accessPoints = [ap["value"] for ap in accessPoints]
        if len(accessPoints) < num:
            return [ap["bssid"] for ap in accessPoints]
        sortedAccessPoints = sorted(accessPoints, key=lambda value: -value["level"])
        return [ap["bssid"] for ap in sortedAccessPoints[0:num]]

def getTopAccessPointsForUser(ids):
    #funf = connection[getDBName(profile)]["funf"]
    currentTime = time.time()
    today = date.fromtimestamp(currentTime)
    firstTime = time.mktime((today - timedelta(days=3)).timetuple())
    startTimes = [start for start in range(int(firstTime), int(currentTime) - 3600*4, 600)]

    allTopAccessPoints = []

    for startTime in startTimes:
        topAccessPoints = getTopAccessPointsForTimeRange(ids, startTime, startTime + 600)
        if topAccessPoints is not None:
            allTopAccessPoints.extend(topAccessPoints)
    return set(sorted(allTopAccessPoints))

def getTopAccessPoints():
    profiles = Profile.objects.all()
    accessPoints = {}
    intersections = {}
    notUnique = {}
    for profile in profiles:
        accessPoints[profile.uuid] = getTopAccessPointsForUser(profile)

    for profile in profiles:
        if len(accessPoints[profile.uuid]) > 0:
            unique = True
            intersections[profile.uuid] = {}
            notUnique[profile.uuid] = []
            maxIntersection = 0
            #print profile.uuid
            for profile2 in profiles:
                intersections[profile.uuid][profile2.uuid] = accessPoints[profile.uuid].intersection(accessPoints[profile2.uuid])
                notUnique[profile.uuid].extend(intersections[profile.uuid][profile2.uuid])
                if profile.uuid <> profile2.uuid:
                    if len(intersections[profile.uuid][profile2.uuid]) > maxIntersection:
                        maxIntersection = len(intersections[profile.uuid][profile2.uuid])
                    if len(intersections[profile.uuid][profile2.uuid]) >= len(accessPoints[profile.uuid]):
                        unique = False
            notUnique[profile.uuid] = set(notUnique[profile.uuid])
            answerCollection = connection[getDBName(profile)]["answer"]
            answerCollection.remove({ "key": "Uniqueness" })
            answer = { "key": "Uniqueness" }
            answer["value"] = { "message": "Your data uniquely identifies you" if unique else "Your data is not unique" }
            answer["value"]["wifi_count"] = len(accessPoints[profile.uuid])
            answer["value"]["unique_wifi_count"] = len(accessPoints[profile.uuid]) - maxIntersection
            answerCollection.save(answer)

