function GET(name) {
	var paramString = window.location.search.substring(1);
	var params = paramString.split('&');
		
	
	for (i in params) {
		var param = params[i];
		var keyVal = param.split('=');
		
		if (keyVal[0] == name) {
			return keyVal[1];
		}
	}
	
	return null;
}

$.ajaxSetup({
    datatype: "json"
});

// this can't just be included in the ajaxsetup step because the backbone-tastypie
// library we're using clears headers on the get request following a put / post
$.ajaxPrefilter( function (options) {
    options.headers = _.extend({ 'bearer_token' : GET('bearer_token') }, options.headers);
    options.url += (options.url.indexOf("?") == -1)? window.location.search : "&" + window.location.search.substring(1);
});

