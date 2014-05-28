from django.shortcuts import render_to_response
from django.template import RequestContext
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib
import pdb

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

