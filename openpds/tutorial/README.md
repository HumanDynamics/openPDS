Tutorial on how to create a new lab.
===================================

1. Updates to openPDS server.
-----------------------------

a. Create a task on openPDS: Write Python code to define a task for the lab`s functionality.
- Example: See *hotspots_tasks.py*

b. Schedule the task on openPDS: Add the task to the Celery scheduler.
- Example: update *oms_pds/celery_settings.py* with the following:

```
    CELERY_IMPORTS = (..., "oms_pds.hotspots_tasks")

    "hotspots-computation": {
        "task": "oms_pds.hotspots_tasks.findHotSpotsTask",
        "schedule": crontab(hour="*", minute="30")
    },
```

c. HTML visualization on openPDS: Write HTML code for lab visualizations.
- Example: See *hotspots.html*

d. JavaScript visualization on openPDS: Write JavaScript code (using backbone.js) for lab visualizations.
- Example: See *hotspots.js*

e. Routing on openPDS: Add path to HTML (visualization) to urls.py file.
- Example: update *oms_pds/visualizations/urls.py* with the following:

```
    urlpatterns = patterns('oms_pds.visualization.views',
        ...,
        (r'^hotspots$', direct_to_template, { 'template' : 'visualization/hotspots.html' }),
    )
```

2. Updates to the MIT mobile client.
-------------------------------------

a. Add the lab to the pds_strings.xml file.
- Example: update pds_strings.xml with the following:

```
    <string name="living_labs_application_list">
		"[
			...,
			{
				'name': 'Hotspots',
				'visualizations': [
					{'title': 'Hotspots of MIT community', 'key': 'hotspots', 'answers': ['hotspots'] }	
				],
				'answers': [ 
					{ 'key': 'hotspots', 'data': ['Simple Location Probe'], 'purpose': ['Heatmaps'] }
				],
				'about': 'Hotspots enables users to view a heatmap of locations frequented by the MIT community.',
				'credits': 'This lab was developed as part of the big data initiative at MIT led by Prof. Sam Madden and Elizabeth Bruce. The Hotspots lab was developed by Sharon Paradesi under the guidance of Dr. Lalana Kagal.'				
			} 
		]"
    </string>
```
