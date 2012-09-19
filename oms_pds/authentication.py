from tastypie.authentication import Authentication
import httplib
import settings
import json


class OAuth2Authentication(Authentication):


    def __get_userinfo_from_token(self, token, scope):
        # upon success, will return a json {'key':'value'}
        userinfo = {}
        try:
            conn = httplib.HTTPConnection(settings.SERVER_OMS_REGISTRY, timeout=100)
            request_path="/get_key_from_token?bearer_token="+str(token)+"&scope="+str(scope)
            conn.request("GET",str(request_path))
            r1 = conn.getresponse()
            response_text = r1.read()
            result = json.loads(response_text)
            print result
            if 'error' in result:
                raise Exception(result['error'])
            key = result['key']
            conn.close()
        except Exception as ex:
            return False
        return key

    def __init__(self, scope):
        self.scope = scope

    def is_authenticated(self, request, **kwargs):
        key = self.__get_userinfo_from_token(request.GET['token'], self.scope)
	
        return True

    def get_identifier(self, request):
        return "jschmitz"


