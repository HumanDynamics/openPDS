from django import forms
from oms_pds.accesscontrol.models import FunfProbeModel

class FunfProbeSettingForm(forms.ModelForm):
	class Meta:
		model = FunfProbeModel
	        exclude = ('funfPK')
