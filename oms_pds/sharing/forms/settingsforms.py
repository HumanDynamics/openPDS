from django import forms
from oms_pds.sharing.models import Tokens, OverallSharingLevel, ProbeGroupSettings
from oms_pds.trust.models import SharingLevel
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple


tokenview = {}
for t in Tokens.objects.all():
    tokenview.update({t.id:t.role.name})

oslview = {}
for osl in OverallSharingLevel.objects.all():
    oslview.update({osl.level:osl.level})

pgsview = {}
for pgs in ProbeGroupSettings.objects.all():
    pgsview.update({pgs.name:pgs.name})

slview = {}
for sl in SharingLevel.objects.all():
    slview.update({sl.level:sl.level})

class Sharing_Form(forms.Form):
    tokens = forms.MultipleChoiceField(tokenview.viewitems(), widget=forms.CheckboxSelectMultiple)
    probes = forms.MultipleChoiceField(pgsview.viewitems(), widget=forms.CheckboxSelectMultiple)
    sharinglevel = forms.MultipleChoiceField(slview.viewitems(), widget=forms.RadioSelect, label= "Overall Sharing Level")


