$(function () {

    window.Sharing = Backbone.Model.extend({
        urlRoot: SHARING_API_URL
    });
 
    window.SharingCollection = Backbone.Collection.extend({
        model: Sharing,
        urlRoot: SHARING_API_URL
    });

    window.SharingView = Backbone.View.extend({
        tagname: "div",
        className: "sharingExpanded",
        
        events: {
            "change .sharingAttribute" : "updateModelFromView",
            "click .saveSharingButton": "saveSharing"
        },

        initialize: function () {
            _.bindAll(this, "updateModelFromView", "saveSharing", "updateModelField", "addOne");
            this.sharing = new Sharing();
            this.sharing.bind("change", this.addOne);
       	    this.sharing.fetch();
	    //this.render();
        },

        render: function () {
//            $(this.el).html(ich.sharingTemplate(this.model.toJSON()));
            $(this.el).html(ich.sharingTemplate(this.sharing));
            return this;
        },
        addOne: function (sharing) { 
            $(this.el).html(ich.sharingTemplate(sharing.attributes));
            return this;
        }, 

        updateModelField: function (model, el) {
            if (el.attr('sharingFieldName').indexOf("overallsharinglevel.") == 0) { 
                var fieldName = el.attr('sharingFieldName').replace("overallsharinglevel.", "");
                var overallsharinglevel = model.get("overallsharinglevel");
                if (!overallsharinglevel) {
                    overallsharinglevel = {};
                }
                overallsharinglevel[fieldName] = this.valueFromElement(el);
                model.set("overallsharinglevel", overallsharinglevel);
            } else {
                model.set(el.attr('sharingFieldName'), this.valueFromElement(el));
            }
        },

        updateModelFromView: function () {
            var me = this;
            this.$('.sharingAttribute').each(function () {
                me.updateModelField(me.model, $(this));
            });
        },

        valueFromElement: function (el) {
            if (el.type == 'checkbox') {
                return el.is(':checked');
            }

            return el.val();
        },

        saveSharing: function () {
            this.model.save();
        }
    });

    window.CreateSharingView = Backbone.View.extend({
        el: "#sharing",

        initialize: function () {
	    _.bindAll(this);
            this.sharing = new Sharing();
            var view = new SharingView({ model : this.sharing });
            $(this.el).append(view.render().el);
            $(this.el).html(view.render().el);
        }
        
//        registerListView: function(sharingListView) {
//            this.sharingListView = sharingListView;
//            this.sharing.on("change:id", this.addToCollectionAndReset);
//        },
//        
//        addToCollectionAndReset: function () {
//            if (this.sharingListView) {
//                this.sharingListView.sharings.add(this.sharing);
//            }
//            this.sharing = new Sharing();
//            this.sharing.on("change:id", this.addToCollectionAndReset);
//            var view = new SharingView({ model : this.sharing });
//            $(this.el).html(view.render().el);
//        }
    });

//    window.SharingListView = Backbone.View.extend({
//        el: "#sharingList", 
//
//        initialize: function () { 
//            _.bindAll(this, "addOne", "addAll");
//            
//            this.sharings = new SharingCollection();
//            this.sharings.bind("add", this.addOne);
//            this.sharings.bind("reset", this.addAll);
//            this.sharings.fetch();
//        },
//         
//        addOne: function (sharing) { 
//            var view = new SharingThumbView({ model : sharing }); 
//            $(this.el).append(view.render().el); 
//        }, 
// 
//        addAll: function () { 
//           this.sharings.each(this.addOne); 
//        },
//    });
    
    window.createSharingView = new CreateSharingView();
//    window.SharingListView = new SharingListView();
//    window.createSharingView.registerListView(window.sharingListView);
});
