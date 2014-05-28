from celery import task
from openpds.core.models import Profile
from openpds.core.internal import getInternalDataStore
from openpds.accesscontrol.models import Optin

def hotSpotsComputation(internal_data_store):
    hot_spots = {}
    location_answer_list = internal_data_store.getAnswerList("recentSimpleLocationProbeByHour")
    location_answer_list = location_answer_list[0]["value"] if location_answer_list.count() > 0 else []
    for location_answer in location_answer_list:
        if location_answer["centroid"]:
	    for location_answer in location_answer["centroid"]:
		centroid = (round(location_answer[0],5), round(location_answer[1],5))
		if centroid in hot_spots:
		    hot_spots[centroid] = hot_spots[centroid] + 1
		else:
		    hot_spots[centroid] = 1
    return hot_spots

@task()
def findHotSpotsTask():
    profiles = Profile.objects.all()

    hot_spots_frequencies = {}
    for profile in profiles:

        try:
            optin_object = Optin.objects.get(datastore_owner = profile, app_id = "Living Lab", lab_id = "MIT-FIT")
        except Optin.DoesNotExist:
            optin_object = None

        if optin_object:
            if optin_object.data_aggregation == 0:
                continue

        internal_data_store = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")
        hot_spots_of_user = hotSpotsComputation(internal_data_store)

	for hot_spot_of_user in hot_spots_of_user:
	    if hot_spot_of_user in hot_spots_frequencies:
		hot_spots_frequencies[hot_spot_of_user] = hot_spots_frequencies[hot_spot_of_user] + 1
	    else:
		hot_spots_frequencies[hot_spot_of_user] = 1

    hot_spots_frequencies_list = []
    for hot_spot in hot_spots_frequencies:
        hot_spot_frequency = { "lat": hot_spot[0], "lng": hot_spot[1], "frequency": hot_spots_frequencies[hot_spot]}
        hot_spots_frequencies_list.append(hot_spot_frequency)

    for profile in profiles:
        internal_data_store = getInternalDataStore(profile, "Living Lab", "Frequent Locations", "")
        internal_data_store.saveAnswer("hotspots", hot_spots_frequencies_list)
