from tastypie.authentication import Authentication


class OAuth2Authentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        return True

    def get_identifier(self, request):
        return "jschmitz"


