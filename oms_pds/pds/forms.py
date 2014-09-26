from django import forms
#from oms_pds.pds.models import QuestionInstance
"""
def binaryUISetup(self, pk):
  self.fields['answer'].widget.attrs['type'] = "range"
  self.fields['pk'].initial = pk

def sliderUISetup(self, pk):
  pass

def multipleChoiceUISetup(self, pk):
  pass

QUESTION_TYPE_UI_SETUP = {
  'b': binaryUISetup,
  's': sliderUISetup,
  'm': multipleChoiceUISetup,
}

class QuestionForm(forms.Form):
  pk = forms.IntegerField()
  answer = forms.IntegerField(widget=forms.HiddenInput)
  
  def setup(self, questionInstance):
    QUESTION_TYPE_UI_SETUP[questionInstance.question_type.ui_type](self, questionInstance.pk)
      
"""
