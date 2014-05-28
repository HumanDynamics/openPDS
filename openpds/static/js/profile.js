window.Profile = Backbone.Model.extend({
    urlRoot: PROFILE_API_URL
});

window.ProfileCollection = Backbone.Collection.extend({
    model: Profile,
    urlRoot: PROFILE_API_URL,

    initialize: function (models, options) {
        this.options = options;
    },

    fetch: function (options) {
        options || (options = {});
        options.data || (options.data = {});
        this.options || (this.options = { })
        //filterMapping = { "u": this.options.email }
        options.data = _.extend(options.data, this.options);
        // Note: we probably want to make this configurable, for the cases where we might be hosting survey questions on the PDS
        options.dataType = "jsonp";
        return Backbone.Collection.prototype.fetch.call(this,options);
    }
});
