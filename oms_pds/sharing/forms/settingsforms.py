from django import forms
from oms_pds.sharing.models import Tokens, OverallSharingLevel, ProbeGroupSetting
from oms_pds.trust.models import SharingLevel, Role
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple


#tokenview = {}
#for t in Tokens.objects.all():
#    tokenview.update({t.id:t.role.name})

oslview = {}
for osl in OverallSharingLevel.objects.all():
    oslview.update({osl.level:osl.level})

pgsview = {}
for pgs in ProbeGroupSetting.objects.all():
    pgsview.update({pgs.name:pgs.name})

slview = {}
for sl in SharingLevel.objects.all():
    slview.update({sl.level:sl.level})

rview = {}
for r in Role.objects.all():
    rview.update({r.name:r.name})

class Sharing_Form(forms.Form):
    #tokens = forms.MultipleChoiceField(tokenview.viewitems(), widget=forms.CheckboxSelectMultiple)
    probes = forms.MultipleChoiceField(pgsview.viewitems(), widget=forms.CheckboxSelectMultiple)
    roles = forms.MultipleChoiceField(rview.viewitems(), widget=forms.CheckboxSelectMultiple)
    sharinglevel = forms.MultipleChoiceField(slview.viewitems(), widget=forms.RadioSelect, label= "Overall Sharing Level")

class CreateSharingForm(forms.Form):

    probes = forms.MultipleChoiceField(pgsview.viewitems(), widget=forms.CheckboxSelectMultiple)
    roles = forms.MultipleChoiceField(rview.viewitems(), widget=forms.CheckboxSelectMultiple)
    sharinglevel = forms.MultipleChoiceField(slview.viewitems(), widget=forms.RadioSelect, label= "Overall Sharing Level")

    @property
    def helper(self):
        form = CreateSharingForm()
        helper = FormHelper()
        reset = Reset('','Reset')
        helper.add_input(reset)
        submit = Submit('','Submit')
        helper.add_input(submit)
        helper.form_action = '/sharing/update'
        helper.form_method = 'POST'
        return helper

