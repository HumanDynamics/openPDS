from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib
import pdb, datetime, re
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

def questionsPage(request):
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
                q.answer = value
                q.expired = True
                q.save()
            refresh = True
    if refresh:
        return HttpResponseRedirect(reverse(questionsPage) +"?bearer_token="+token+"&datastore_owner="+datastore_owner_uuid)
        
    questions = QuestionInstance.objects.filter(expired=False, profile=datastore_owner).order_by("-datetime")
    questionsRemainingList = []
    for q in questions:
        expiry = q.datetime + datetime.timedelta(minutes=q.question_type.expiry)
        if q.answer != None or expiry.replace(tzinfo=None) < datetime.datetime.now():
            q.expired = True
            q.save()
        else:
            questionsRemainingList.append((q, q.question_type.optionList()))
    
    return render_to_response("visualization/smartcatch_questions.html", {
        "questions": questionsRemainingList,
        "bearer_token": token,
        "datastore_owner": datastore_owner_uuid,
    }, context_instance=RequestContext(request))
