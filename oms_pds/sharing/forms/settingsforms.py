from django import forms
from oms_pds.sharing.models import Tokens, OverallSharingLevel, ProbeGroupSetting
from oms_pds.pds.models import SharingLevel, Role
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple


#tokenview = {}
#for t in Tokens.objects.all():
#    tokenview.update({t.id:t.role.name})

oslview = {}
pgsview = {}
slview = {}
rview = {}


class Sharing_Form(forms.Form):
    #tokens = forms.MultipleChoiceField(tokenview.viewitems(), widget=forms.CheckboxSelectMultiple)
    probes = forms.MultipleChoiceField(pgsview.viewitems(), widget=forms.CheckboxSelectMultiple)
    roles = forms.MultipleChoiceField(rview.viewitems(), widget=forms.CheckboxSelectMultiple)
    sharinglevel = forms.MultipleChoiceField(slview.viewitems(), widget=forms.RadioSelect, label= "Overall Sharing Level")
    def update_form(self, uuid):
        new_pgsview = {}
        new_slview = {}
        new_rview = {}
        for pgs in ProbeGroupSetting.objects.all():#(datastore_owner_id=uuid):
            new_pgsview.update({pgs.name:pgs.name})
        
        for sl in SharingLevel.objects.filter(datastore_owner_id=uuid):
            new_slview.update({sl.level:sl.level})
        
        for r in Role.objects.filter(datastore_owner_id=uuid):
            new_rview.update({r.name:r.name})

	self.fields['roles'] = forms.MultipleChoiceField(new_rview.viewitems(), widget=forms.CheckboxSelectMultiple)
	self.fields['probes'] = forms.MultipleChoiceField(new_pgsview.viewitems(), widget=forms.CheckboxSelectMultiple)
	self.fields['sharinglevel'] = forms.MultipleChoiceField(new_slview.viewitems(), widget=forms.RadioSelect, label= "Overall Sharing Level")
#    probes = None
#    roles = None
#    sharinglevel = None
    
#        self.probes = forms.MultipleChoiceField(pgsview.viewitems(), widget=forms.CheckboxSelectMultiple)
#        self.roles = forms.MultipleChoiceField(rview.viewitems(), widget=forms.CheckboxSelectMultiple)
#        self.sharinglevel = forms.MultipleChoiceField(slview.viewitems(), widget=forms.RadioSelect, label= "Overall Sharing Level")

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

