from django.contrib import admin
from oms_pds.pds.models import Profile, QuestionType, QuestionInstance 

admin.site.register(Profile)
admin.site.register(QuestionType)
admin.site.register(QuestionInstance)