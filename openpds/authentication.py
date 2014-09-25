from tastypie.authentication import Authentication
import httplib
import settings
import json
import pdb

class OAuth2Authentication(Authentication):

    def get_userinfo_from_token(self, token, scope):
        # upon success, will return a json {'key':'value'}
        #print "get_userinfo_from_token"
        userinfo = {}
        try:
            conn = httplib.HTTPConnection(settings.REGISTRY_SERVER, timeout=100)
            request_path="/get_key_from_token?bearer_token="+str(token)+"&scope="+str(scope)
            conn.request("GET",str(request_path))
            r1 = conn.getresponse()
            response_text = r1.read()
            result = json.loads(response_text)
            if 'error' in result:
                raise Exception(result['error'])
            key = result['key']
            conn.close()
        except Exception as ex:
            print ex
            return False
        return key

    def __init__(self, scope):
        self.scope = scope

    def is_authenticated(self, request, **kwargs):
        token = request.GET['bearer_token'];
        return self.get_userinfo_from_token(token, self.scope) is not False

    def get_identifier(self, request):
        return request.GET.get('datastore_owner')


