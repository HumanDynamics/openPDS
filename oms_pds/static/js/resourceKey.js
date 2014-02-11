window.ResourceKey = Backbone.Model.extend({
    urlRoot: RESOURCE_KEY_API_URL    
});

window.ResourceKeyCollection = Backbone.Collection.extend({
    model: ResourceKey,
    urlRoot: RESOURCE_KEY_API_URL,
    
    initialize: function (models, options) {
        this.options = options;
    },

    fetch: function (options) {
        options || (options = {});
        options.data || (options.data = {});
        this.options || (this.options = { key: ANSWERLIST_KEY })
        filterMapping = { "key": this.options.key }
        options.data = _.extend(options.data, filterMapping);

        return Backbone.Collection.prototype.fetch.call(this,options);
    }
});

window.ResourceKeySharingView = Backbone.View.extend({
    el: "<div data-role='fieldcontain'>",
    
    bindAll: function () {  
         _.bindAll(this, "render", "saveAnswer", "selectedValue");
    },

    initialize: function (surveyQuestion) {
        this.bindAll();
        
        this.resourceKeys = new ResourceKeyCollection();
        
    },

    render: function () {
    }
});

