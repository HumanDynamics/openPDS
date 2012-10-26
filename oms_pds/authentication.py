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
	    print ex
            return False
        return key

    def __init__(self, scope):
        self.scope = scope

    def is_authenticated(self, request, **kwargs):
	token = request.GET['bearer_token'];
	print token
	print self.scope
	
#       key = self.__get_userinfo_from_token(token, self.scope)
#	print "-----key-----"
#	print key	
	
#	settings.MONGODB_DATABASE = "User_"+str(key)
	
        return True

    def get_identifier(self, request):
        return "jschmitz"


