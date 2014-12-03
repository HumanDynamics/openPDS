from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib
from oms_pds.pds.internal import getInternalDataStore
import pdb, datetime, re, time, math
from oms_pds.pds.models import Profile, QuestionInstance, QuestionType
from django.core.urlresolvers import reverse

def places(request):
    template = {}
#    pdb.set_trace()
    if "place" in request.GET:
        place = request.GET["place"]
        placeUri = "http://linkedgeodata.org/triplify/%s" % place
        query = """
            prefix geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> 
            Select ?lat ?long 
            From <http://linkedgeodata.org> { 
              <%s> geo:lat ?lat . 
              <%s> geo:long ?long . 
            }""" % (placeUri, placeUri)
        query = query.replace("    ", "").replace("\n", "")
        sparql = SPARQLWrapper("http://live.linkedgeodata.org/sparql")
        sparql.setReturnFormat(JSON)   #pdb.set_trace()
        sparql.setQuery(query)
        results = sparql.query().convert()
        latlongs = [(result["lat"]["value"], result["long"]["value"]) for result in results["results"]["bindings"]]
        if len(latlongs) > 0:
            lat = latlongs[0][0]
            lng = latlongs[0][1]
            template["lat"] = float(lat)
            template["long"] = float(lng)
#        placeGraph = Graph()
#        placeGraph.parse(placeUri)
#        subj = rdflib.term.URIRef(placeUri)
#        geo = rdflib.Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
#        #latlong = placeGraph.query("select ?lat ?long where { ?place geo:lat ?lat . ?place geo:long ?long }")
#        if (None, geo["lat"], None) in placeGraph and (None, geo["long"], None) in placeGraph:
#            template["lat"] = float(placeGraph.value(subject=subj, predicate=geo["lat"]))
#            template["long"] = float(placeGraph.value(subject=subj, predicate=geo["long"]))
    
    return render_to_response("visualization/locationMap.html", template, RequestContext(request))

def smartcatchQuestionsPage(request):
    token = request.GET['bearer_token']
    datastore_owner_uuid = request.GET["datastore_owner"]
    datastore_owner, ds_owner_created = Profile.objects.get_or_create(uuid = datastore_owner_uuid)
    #TODO need to check that the token is in scope
    
    refresh = False
    for key in request.GET:
        if re.search('^q_', key) != None:
            pk = int(re.sub(r'^q_', '', key))
            value = request.GET[key]
            q = QuestionInstance.objects.filter(pk=pk)
            if value != "" and q.count() > 0 and q[0].expired == False:
                q = q[0]
                q.answer = int(float(value))
                q.save()
                refresh = True
    if refresh:
        return HttpResponseRedirect(reverse(smartcatchQuestionsPage) +"?bearer_token="+token+"&datastore_owner="+datastore_owner_uuid)
        
    questions = QuestionInstance.objects.filter(expired=False, answer__isnull=True, profile=datastore_owner).order_by("-datetime")
    questionsRemainingList = []
    for q in questions:
        expiry = q.datetime + datetime.timedelta(minutes=q.question_type.expiry)
        if expiry.replace(tzinfo=None) < datetime.datetime.now():
            q.expired = True
            q.save()
        else:
            questionsRemainingList.append((q, q.question_type.optionList()))

    try:
        #weeks = internalDataStore.getAnswerList("activityScoreHistory")[0]['value'][0]["time"]
        weeks = datastore_owner.created
        weeks = math.ceil((time.time() - weeks) / (60 * 60 * 24 * 7))
    except:
        weeks = 1
    
    return render_to_response("visualization/smartcatch_questions.html", {
        "questions": questionsRemainingList,
        "bearer_token": token,
        "datastore_owner": datastore_owner_uuid,
        'weeksSinceStart': weeks,
    }, context_instance=RequestContext(request))
    
MOREINFO_GOAL_URL = {
    's': 'http://www.lung.org/stop-smoking/',
    'e': 'http://www.choosemyplate.gov/healthy-eating-tips.html',
    't': 'http://www.mayoclinic.org/healthy-living/stress-management/in-depth/relaxation-technique/art-20045368',
    'f': 'http://www.diabetes.org/living-with-diabetes/complications/foot-complications/foot-care.html',
    'n': 'N/A'
}
    
def smartcatchMyResults(request):
    datastore_owner_uuid = request.GET["datastore_owner"]
    profile, ds_owner_created = Profile.objects.get_or_create(uuid = datastore_owner_uuid)
    
    #TODO right now the bearer_token is not being checked. This must be checked.
    internalDataStore = getInternalDataStore(profile, "MGH smartCATCH", "Social Health Tracker", "")
    
    try:
        avgs = internalDataStore.getAnswer("socialhealthavgs")[0]['value']
        socialhealth = internalDataStore.getAnswer("socialhealth")[0]['value']
        surveyscores = internalDataStore.getAnswer("surveyscores")[0]['value']
    except:
        return HttpResponse("Not enough data collected. Please wait.")
    
    try:
        weeks = profile.created
        #weeks = internalDataStore.getAnswerList("activityScoreHistory")[0]['value'][0]["time"]
        weeks = math.ceil((time.time() - weeks) / (60 * 60 * 24 * 7))
    except:
        weeks = 1
    
    moreinfo_goal_url = MOREINFO_GOAL_URL[profile.goal]
    
    return render_to_response("visualization/smartcatch_myresults.html", {
        'socialhealth': socialhealth,
        'surveyscores': surveyscores,
        'avgActivity': avgs["activity"],
        'avgSocial': avgs["social"],
        'avgFocus': avgs["focus"],
        'avgSleep': avgs["sleep"],
        'avgGlucose': avgs["glucose"],
        'avgMeds': avgs["meds"],
        'avgGoal': avgs["goal"],
        'weeksSinceStart': weeks,
        'goaltype': profile.goal,
        'control': profile.study_status == 'c',
        'moreinfo_goal_url': moreinfo_goal_url,
    }, context_instance=RequestContext(request))
    
def smartcatchSplash(request):
    datastore_owner_uuid = request.GET["datastore_owner"]
    profile, ds_owner_created = Profile.objects.get_or_create(uuid = datastore_owner_uuid)
    
    #TODO right now the bearer_token is not being checked. This must be checked.
    internalDataStore = getInternalDataStore(profile, "MGH smartCATCH", "Social Health Tracker", "")
    
    try:
        avgs = internalDataStore.getAnswer("socialhealthavgs")[0]['value']
        socialhealth = internalDataStore.getAnswer("socialhealth")[0]['value']
        surveyscores = internalDataStore.getAnswer("surveyscores")[0]['value']
    except:
        return HttpResponse("Not enough data collected. Please wait.")
    
    return render_to_response("visualization/smartcatch_splash.html", {
        'socialhealth': socialhealth,
        'surveyscores': surveyscores,
        'avgActivity': avgs["activity"],
        'avgSocial': avgs["social"],
        'avgFocus': avgs["focus"],
        'avgSleep': avgs["sleep"],
        'avgGlucose': avgs["glucose"],
        'avgMeds': avgs["meds"],
        'avgGoal': avgs["goal"],
        'control': profile.study_status == 'c',
    }, context_instance=RequestContext(request))
    
def smartcatchHistory(request):
    datastore_owner_uuid = request.GET["datastore_owner"]
    profile, ds_owner_created = Profile.objects.get_or_create(uuid = datastore_owner_uuid)
    
    #TODO right now the bearer_token is not being checked. This must be checked.
    internalDataStore = getInternalDataStore(profile, "MGH smartCATCH", "Social Health Tracker", "")
    
    try:
        avgs = internalDataStore.getAnswer("socialhealthavgs")[0]['value']
        socialhealth = internalDataStore.getAnswer("socialhealth")[0]['value']
        surveyscores = internalDataStore.getAnswer("surveyscores")[0]['value']
        sleepScoreHistory = internalDataStore.getAnswerList("sleepScoreHistory")[0]['value']
        glucoseScoreHistory = internalDataStore.getAnswerList("glucoseScoreHistory")[0]['value']
        medsScoreHistory = internalDataStore.getAnswerList("medsScoreHistory")[0]['value']
        activityScoreHistory = internalDataStore.getAnswerList("activityScoreHistory")[0]['value']
        socialScoreHistory = internalDataStore.getAnswerList("socialScoreHistory")[0]['value']
        focusScoreHistory = internalDataStore.getAnswerList("focusScoreHistory")[0]['value']
        goalScoreHistory = internalDataStore.getAnswerList("goalScoreHistory")[0]['value']
        activityScoreGroupHistory = internalDataStore.getAnswerList("activityScoreGroupHistory")[0]['value']
        socialScoreGroupHistory = internalDataStore.getAnswerList("socialScoreGroupHistory")[0]['value']
        focusScoreGroupHistory = internalDataStore.getAnswerList("focusScoreGroupHistory")[0]['value']
        sleepScoreGroupHistory = internalDataStore.getAnswerList("sleepScoreGroupHistory")[0]['value']
        glucoseScoreGroupHistory = internalDataStore.getAnswerList("glucoseScoreGroupHistory")[0]['value']
        medsScoreGroupHistory = internalDataStore.getAnswerList("medsScoreGroupHistory")[0]['value']
        goalScoreGroupHistory = internalDataStore.getAnswerList("goalScoreGroupHistory")[0]['value']
    except:
        return HttpResponse("Not enough data collected. Please wait.")
        
    currentTime = time.time();
    
    return render_to_response("visualization/smartcatch_history.html", {
        'socialhealth': socialhealth,
        'surveyscores': surveyscores,
        'avgActivity': avgs["activity"],
        'avgSocial': avgs["social"],
        'avgFocus': avgs["focus"],
        'avgSleep': avgs["sleep"],
        'avgGlucose': avgs["glucose"],
        'avgMeds': avgs["meds"],
        'avgGoal': avgs["goal"],
        'sleepScoreHistory': sleepScoreHistory,
        'glucoseScoreHistory': glucoseScoreHistory, 
        'medsScoreHistory': medsScoreHistory,
        'activityScoreHistory': activityScoreHistory,
        'socialScoreHistory': socialScoreHistory,
        'focusScoreHistory': focusScoreHistory,
        'goalScoreHistory': goalScoreHistory,
        'activityScoreGroupHistory': activityScoreGroupHistory,
        'socialScoreGroupHistory': socialScoreGroupHistory,
        'focusScoreGroupHistory': focusScoreGroupHistory,
        'goalScoreGroupHistory': goalScoreGroupHistory,
        'medsScoreGroupHistory': medsScoreGroupHistory,
        'glucoseScoreGroupHistory': glucoseScoreGroupHistory,
        'sleepScoreGroupHistory': sleepScoreGroupHistory,
        'dayCutoff': currentTime - 24 * 3600,
        'weekCutoff': currentTime - 7 * 24 * 3600,
        'monthCutoff': currentTime - 30 * 24 * 3600,
        'goaltype': profile.goal,
        'control': profile.study_status == 'c',
    }, context_instance=RequestContext(request))
    
def smartcatchHelp(request):
    return render_to_response("visualization/smartcatch_help.html", {
    }, context_instance=RequestContext(request))
    
