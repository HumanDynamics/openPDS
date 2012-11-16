from tastytools.api import Api
from oms_pds.pds.api import FunfResource, FunfConfigResource, RoleResource, PurposeResource, AnswerResource, AnswerListResource

v1_api = Api(api_name='personal_data')
v1_api.register(FunfResource())
v1_api.register(FunfConfigResource())
v1_api.register(RoleResource())
v1_api.register(PurposeResource())
v1_api.register(AnswerResource())
v1_api.register(AnswerListResource())


