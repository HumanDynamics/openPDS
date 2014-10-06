#from tastytools.api import Api
from tastypie.api import Api

from openpds.core.api import FunfResource, FunfConfigResource, AnswerResource, AnswerListResource, AuditEntryResource, AuditEntryCountResource, NotificationResource, DeviceResource,IncidentResource
from openpds.meetup.api import MeetupRequestResource
v1_api = Api(api_name='personal_data')
v1_api.register(FunfResource())
v1_api.register(FunfConfigResource())
v1_api.register(AnswerResource())
v1_api.register(AnswerListResource())
v1_api.register(AuditEntryResource())
v1_api.register(AuditEntryCountResource())
v1_api.register(NotificationResource())
v1_api.register(DeviceResource())
v1_api.register(IncidentResource())
v1_api.register(MeetupRequestResource())
