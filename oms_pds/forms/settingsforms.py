from django import forms
from oms_pds.trust.models import Scope, Role, SharingLevel
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple


scopeview = {}
for s in Scope.objects.all():
    scopeview.update({s.name:s.name})

roleview = {}
for r in Role.objects.all():
    roleview.update({r.name:r.name})

sharingview = {}
for sl in SharingLevel.objects.all():
    sharingview.update({sl.level:sl.level})

class PermissionsForm(forms.Form):
    groups = forms.MultipleChoiceField(roleview.viewitems(), widget=forms.CheckboxSelectMultiple)
    sensors = forms.MultipleChoiceField()
    sharinglevel = forms.MultipleChoiceField(sharingview.viewitems(), widget=forms.CheckboxSelectMultiple, label= "Sharing Level")

class Purpose_Form(forms.Form):
    purpose = forms.CharField(max_length=100)
    scopes = forms.MultipleChoiceField(scopeview.viewitems(), widget=forms.CheckboxSelectMultiple)
    roles = forms.MultipleChoiceField(roleview.viewitems(), widget=forms.CheckboxSelectMultiple)
    sharinglevels = forms.MultipleChoiceField(sharingview.viewitems(), widget=forms.CheckboxSelectMultiple, label= "Sharing Levels")
