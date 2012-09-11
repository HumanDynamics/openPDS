from tastypie.authorization import Authorization


class PDSAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        get_key_from_token(request.token,request.scope)
	return True
    def get_key_from_token(token, scope):
        # upon success, will return a json {'key':'value'}
        logging.debug('getting key from token')
        key = ""
        try:
            conn = httplib.HTTPConnection(registryServer, timeout=100)
            request_path="/get_key_from_token?bearer_token="+str(token)+"&scope="+str(scope)
            conn.request("GET",str(request_path))
            r1 = conn.getresponse()
            response_text = r1.read()
            result = json.loads(response_text)
            if 'error' in result:
                raise Exception(result['error'])
            logging.debug(result)
            key = result['key']
            conn.close()
        except Exception as ex:
            logging.debug(ex)
            return False
        return key

    # Optional but useful for advanced limiting, such as per user.
    # def apply_limits(self, request, object_list):
    #    if request and hasattr(request, 'user'):
    #        return object_list.filter(author__username=request.user.username)
    #
    #    return object_list.none()
