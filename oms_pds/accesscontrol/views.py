from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms

def funfProbeSettingView(request):
	if request.method=="POST":
		form = FunfProbeSettingForm(request.POST)
      		if form.is_valid():
            		selected = form.cleaned_data.get(‘selected’)
            		#write to model?
    	else:
        	form = FunfProbeSettingForm

    	return render_to_response('funfsettings.html', {'form':form },
        			  context_instance=RequestContext(request))
