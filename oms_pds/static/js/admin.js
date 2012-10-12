
$.ajaxSetup({
    datatype: "json"
});

// this can't just be included in the ajaxsetup step becuase the backbone-tastypie
// library we're using clears headers on the get request following a put / post
$.ajaxPrefilter( function (options) {
    options.headers = _.extend({ 'token' : '1234' }, options.headers)
});


