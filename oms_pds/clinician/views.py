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
from django.db.models import Avg, StdDev
import json
import random


####
# FOR TESTING
####
def breakdown_history_test(scores):
    scores = [{'score': random.random() * 100} for r in xrange(100)]
    return breakdown_history(scores)
###############


def breakdown_history(scores):
    """breaks down the users' scores to individual percentages for
    "good", "medium", and "bad".

    returns a dict of the form:
    {'good': <percent_good>
    'medium': <percent_medium>
    'bad': <percent_bad>}
    """
    scores = [s['score'] for s in scores]
    percents = {'good': [s for s in scores if s >= 70],
                'medium': [s for s in scores if s >= 50 and s < 70],
                'bad': [s for s in scores if s < 50]}

    return [{'status': k,
             'score': len(v) / float(len(scores))} for k, v in percents.items()]


def groupOverview(request):
    """gets the group overview page.

    Request params:

    patient_status: one of {'i', 'c', 'b'}. i for intervention, c for
    control, b for both.

    renders the page with:
    {'participant_data': [{<uuid>: {'meds': {'good': <%>, 'medium': <%>, 'bad': <%>}, ...}}]}

    """
    # patient_status = [request.GET['patient_status']]
    # if patient_status == ['b']:
    #     patient_status = ['i', 'c']

    allParticipants = Profile.objects.filter(study_status__in=['i', 'c'])

    goal_map = {'f': 'Foot Care',
                's': 'Smoking',
                'e': 'Eating Healthy',
                't': 'Stress Level'}

    participant_data = []
    for p in allParticipants:
        ids = getInternalDataStore(p, "MGH smartCATCH", "Social Health Tracker", "")
        try:
            sleepScoreHistory = ids.getAnswerList("sleepScoreHistory")[0]['value']
            glucoseScoreHistory = ids.getAnswerList("glucoseScoreHistory")[0]['value']
            medsScoreHistory = ids.getAnswerList("medsScoreHistory")[0]['value']
            activityScoreHistory = ids.getAnswerList("activityScoreHistory")[0]['value']
            socialScoreHistory = ids.getAnswerList("socialScoreHistory")[0]['value']
            focusScoreHistory = ids.getAnswerList("focusScoreHistory")[0]['value']
            goalScoreHistory = ids.getAnswerList("goalScoreHistory")[0]['value']
        except:
            continue

        obj = {'Sleep': sleepScoreHistory,
               'Glucose': glucoseScoreHistory,
               'Medications': medsScoreHistory,
               'Activity': activityScoreHistory,
               'Social': socialScoreHistory,
               'Focus': focusScoreHistory,
               goal_map[p.goal]: goalScoreHistory}

        # dict of {key: {'good': <%> 'medium': <%>, 'bad': <%>}, ...}
        obj = {k: breakdown_history_test(v) for k, v in obj.items()}
        obj['uid'] = p.uuid

        participant_data.append(obj)
        for n in xrange(10):
            obj2 = obj.copy()
            obj2['uid'] = "test-{}".format(n)
            participant_data.append(obj2)

    return render_to_response("clinician/group_overview.html",
                              {'num_participants': len(participant_data),
                               'participant_data': json.dumps(participant_data)},
                              context_instance=RequestContext(request))

def patientInfo():
    uid = request.GET['user_id']

    # shot in the dark
    profile = Profile.objects.filter(uuid__in=['i', 'c'])

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
