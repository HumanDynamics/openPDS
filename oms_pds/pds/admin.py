from django.contrib import admin
from oms_pds.pds.models import Profile, QuestionType, QuestionInstance, AuditEntry


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'study_status', 'goal', 'created']
    search_fields = ['uuid', 'study_status', 'goal']
    list_editable = ['study_status', 'goal']
    list_filter = ['study_status', 'goal']

class QuestionInstanceAdmin(admin.ModelAdmin):
    list_display = ['question_type', 'profile', 'expired', 'datetime', 'answer']
    list_filter = ['expired', 'datetime', 'question_type']
    search_fields = ['profile__uuid']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(QuestionType)
admin.site.register(QuestionInstance, QuestionInstanceAdmin)
admin.site.register(AuditEntry)