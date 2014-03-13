window.MeetupRequest = Backbone.Model.extend({
    urlRoot: MEETUP_REQUEST_API_URL
});

window.MeetupRequestCollection = Backbone.Collection.extend({
    model: MeetupRequest,
    urlRoot: MEETUP_REQUEST_API_URL,

    initialize: function (models, options) {
        this.options = (options)? options:{};
    },

    fetch: function (options) {
        options || (options = {});
        options.data || (options.data = {});
        
        if (typeof(this.options.uuid) !== "undefined") {
            filterMapping = { "uuid": this.options.uuid }
            options.data = _.extend(options.data, filterMapping);
        }

        return Backbone.Collection.prototype.fetch.call(this,options);
    }
});

window.MeetupRequestView = Backbone.View.extend({
    tagName: "li",
    className: "meetup-request",
    
    initialize: function (options) {
        _.bindAll(this, "render", "hide", "profilesReset");
        this.rendered = false;
        this.model.on("change", this.render);
        this.model.on("destroy", this.hide);
        this.uuid = GET("datastore_owner");
        this.profilesReady = false;
        if (options.profiles) {
            if (options.profiles.length > 0) {
                this.profilesReset(options.profiles);
            } else {
                options.profiles.bind("reset", this.profilesReset);
            }
        }
    },

    hide: function () {
        $(this.el).hide("fast");
    },
    
    profilesReset: function (profiles) {
        this.profiles = profiles;
        this.render();
    },

    getUserText: function (uuid) {
        return (uuid == this.uuid)? "Me":((this.profiles)? this.profiles.find(function (p) { return p.get("uuid") == uuid; }).get("user").email : uuid);
    },
    
    getMapLink: function (place) {
        return "<a href='http://maps.google.com/maps?z=12&t=m&q=loc:"+place[0]+"+"+place[1]+"' target='_blank'>("+place[0].toFixed(4)+", "+place[1].toFixed(4)+")</a>";
    },
    
    render: function () {
        var me = this;
        var description = this.model.get("description");
        var requester = this.model.get("requester");
        var participants = this.model.get("participants");
        var approved = this.model.get("approved");
        var time = this.model.get("time");
        var place = this.model.get("place");
        var uuid = this.model.get("uuid");
        var requesterText = this.getUserText(requester);
        var approvedText = (approved)? "Waiting on participants to approve...":"Must be approved first!";
        var timePlaceText = (time && place)? time + ":00 at "+this.getMapLink(place):"TBD ("+approvedText+")";
        var participantsText = requesterText+", "+_.map(participants, function (u) { return me.getUserText(u); }).join(", ");
        var mapView = (time && place && uuid)? new AnswerListMap(null, [place[0], place[1]], "map"+uuid):null;
        if (!this.rendered) {
            var subject = $("<div class='meetup-request-subject'></div>").text(description);
            this.from = $("<div class='meetup-request-from'></div>");
            this.who = $("<div class='meetup-request-who'></div>");
            this.where = $("<div class='meetup-request-location'></div>");
            this.map = $("<div class='meetup-request-map' style='height: 50px'></div>");
            var actions = $("<div data-role='controlgroup' data-type='horizontal' data-mini='true'></div>");
            this.approveButton = $("<button>Approve</button>").click(function (e) { 
                me.model.save({ approved: true });
            });
            this.denyButton = $("<button>Deny</button>").click(function (e) {
                me.model.save({ approved: false });
            });
            this.deleteButton = $("<button>Delete</button>").click(function (e) {
                $(this).addClass("ui-disabled");
                me.model.destroy();
            });
            actions.append(this.approveButton);
            actions.append(this.denyButton);
            actions.append(this.deleteButton);
            actions.controlgroup();
            this.$el.append(subject);
            this.$el.append(this.from);
            this.$el.append(this.who);
            this.$el.append(this.where);
            this.$el.append(this.map);
            this.$el.append(actions);
        }
        
        this.from.text("From: "+requesterText);
        this.who.text("With: "+participantsText);
        this.where.html("Time & Place: "+timePlaceText);
        if (mapView) {
            this.map.attr("id", "map"+uuid);
        }
        if (approved) {
            this.approveButton.addClass("ui-disabled");
            this.denyButton.addClass("ui-disabled");
        }
        this.rendered = true;
        return $(this.el);
    }
});

window.MeetupRequestCollectionView = Backbone.View.extend({ 
    tagName: "ul",
    className: "meetup-request-collection",
    attributes: {"data-role": "listview", "data-inset": "false", "data-filter": "true", "data-theme": "a", "data-filter-placeholder": "Filter Meetups..." },
    
    initialize: function (options) {
        _.bindAll(this, "render", "collectionReset", "addMeetup");
        this.container = options.container;
        if (options.profiles) {
            this.profiles = options.profiles;
        }
        if (!this.collection) {
            this.collection = new MeetupRequestCollection();
            this.collection.bind("reset", this.collectionReset);
            this.collection.fetch();
        } else {
            this.collection.bind("reset", this.collectionReset);
        }

        this.collection.on("add", this.addMeetup);
        this.periodicUpdating = false;
        this.render();
    },

    addMeetup: function (model) {
        var mrView = new MeetupRequestView({ model: model, profiles: this.profiles });
        $(this.el).append(mrView.render());
        $(this.el).listview("refresh");
    },

    collectionReset: function () {
        var me = this;
        $(this.el).empty();
        this.collection.each(function (meetup) {
            var mrView = new MeetupRequestView({ model: meetup, profiles: me.profiles });
            $(me.el).append(mrView.render());
        });
        $(this.el).listview().listview("refresh");
        this.container.trigger("create");
        if (this.periodicUpdating) {
            setInterval(function () {
                me.collection.fetch();
            }, 5000);
            this.periodicUpdating = false;
        }
    },

    render: function () {
        var me = this;
        this.container.append($(this.el));
        this.container.trigger("create");
        return $(this.el);
    }
});

window.CreateMeetupRequestView = Backbone.View.extend({
    tagName: "div",
    
    initialize: function(options) {
        _.bindAll(this, "render", "addCreateButton", "addParticipantTextBox", "createRequest", "setProfilesReady", "removeEmptyTextBoxes");
        options || (options = { autocomplete: false });
        this.autoComplete = options.autocomplete;
        this.container = options.container;
        this.numBoxesAdded = 0;
        this.participants = [];
        this.profilesReady = false;
        if (!this.autoComplete) {
            this.render()
        }
        this.profileCollection = new ProfileCollection([], { limit: 100});
        this.profileCollection.bind("reset", this.setProfilesReady);
        this.profileCollection.fetch();
        if (!this.collection) {
            this.collection = new MeetupRequestCollection();
            //this.requestCollection.bind("reset", this.render);
            this.collection.fetch();
        }
        this.render();
    },
    
    render: function () {
        this.addDescriptionTextBox();
        $(this.el).append($("<div id='meetupParticipantsContainer'>Participant emails:</div>"));
        if (!this.autoComplete) {
            this.addParticipantTextBox(true);
        }
        this.addCreateButton();        
        this.container.append($(this.el));
        $(this.el).trigger("create");
    },
    
    setProfilesReady: function () {
        var me = this;
        this.profilesReady = true;
        this.emails =[];
        this.profileCollection.each(function (p) {
            me.emails.push(p.get("user").email);
        });
        if (this.autoComplete) {
            this.addParticipantTextBox(true);
        }
    },

    allBoxesUsed: function () {
        var allUsed = true;
        $(".meetup-participant").each(function (i,e) {
            if ($(this).val().length == 0) {
                allUsed = false;
            }
        });
        return allUsed;
    },

    removeEmptyTextBoxes: function () {
        var me = this;
        var numBoxes = $(".meetup-participant").length;
        $(".meetup-participant").each(function (i, e) {
            var $this = $(this);
            if ($this.val().length == 0 && i < numBoxes - 1) {
                $("#"+$this.attr("id")+"Container").hide("fast", function () { $(this).remove(); });
            }
        });
    },    

    addParticipantTextBox: function (setFocus) {
        var me = this;
        this.numBoxesAdded++;
        var id = "participant" + this.numBoxesAdded;
        var participantContainer = $("<div id='"+id+"Container"+"'></div>");        
        this.$("#meetupParticipantsContainer").append(participantContainer);

        var participantInput = $("<input type='text' id='"+id+"' class='meetup-participant' />").keyup(function (event) {
           var $this = $(this)
           if ($this.val().length > 0 && me.allBoxesUsed()) {
                me.addParticipantTextBox(false);
            }
        }).blur(function () {
            me.removeEmptyTextBoxes();
        });

        if (setFocus) {
            participantInput.focus();
        }

        participantContainer.append(participantInput);//.trigger("create");

        if (this.autoComplete) {
            var participantUl = $("<ul data-role='listview' data-input='#"+id+"' data-inset='true' data-filter='true' data-filter-reveal='true' data-filter-placeholder='Paricipant email...'></ul>");
            this.profileCollection.each(function (p) {
                var item = $("<li>"+p.get("user").email+"</li>").click(function (event) {
                    me.participants.push($(this).text());
                    participantInput.val($(this).text());
                    participantUl.find("li").addClass("ui-screen-hidden");
                    participantUl.listview("refresh");
                });
                participantUl.append(item);
            });
            participantContainer.append(participantUl);//.trigger("create");
        }
        participantContainer.trigger("create");
        //this.$("#meetupParticipantsContainer").append(participantContainer);
    },
    
    addCreateButton: function () {
        var me = this;
        var createButton = $("<button>create request</button>").click(function (event) {
            me.createRequest();
            return false;
        });
       
        $(this.el).append(createButton);
    },

    addDescriptionTextBox: function () {
        var fields = $("<div data-role='fieldcontain'></div>");
        fields.append($("<label for='description'>Meetup description:</label>"));
        fields.append($("<input type='text' id='description' />"));
        $(this.el).append(fields);
    },
    
    createRequest: function () {
        if (this.profilesReady) {
            var emailRe = /[a-z0-9!#$%&'*+/=?^_{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/;
            var description = $("#description").val();
            var requester = GET("datastore_owner");
            var participants = [];
            var me = this;
            this.$(".meetup-participant").each(function (i, e) {
                var email = $(this).val();
                if (email.length > 0 && emailRe.test(email)) {
                    var profile = me.profileCollection.find(function (p) {
                        return p.get("user").email == email;
                    });
                    if (profile) {
                        participants.push(profile.get("uuid"));
                    }
                }
            });
    
            this.collection.create({
                requester: requester,
                description: description,
                participants: participants,
                approved: true
            });
        } else {
            // Profiles haven't finished loading... maybe queue up the request so it's done in setProfilesReady?
        }
    }
});

window.MeetupRequestDashboardView = Backbone.View.extend({
    tagName: "div",
    
    initialize: function (options) {
        _.bindAll(this, "render");
        this.container = options.container;
        this.collection = new MeetupRequestCollection();
        this.collection.bind("reset", this.render);

        // NOTE: the following must happen in the initialize method so jquery mobile will know what to do when the
        // child views render themselves. Nothing gets added to the DOM until this view's render method is called.
        this.createContainer = $("<div data-role='collapsible' data-collapsed='true'><h3>Request a Meetup</h3></div>");
        this.collectionContainer = $("<div data-role='collapsible' data-collapsed='false'><h3>My Meetups</h3></div>");
        $(this.el).append(this.createContainer);
        $(this.el).append(this.collectionContainer);

        this.createView = new CreateMeetupRequestView({ collection: this.collection, container: this.createContainer, autocomplete: true});
        this.collectionView = new MeetupRequestCollectionView({ collection: this.collection, container: this.collectionContainer, profiles:this.createView.profileCollection });

        this.collection.fetch();
    },

    render: function () {
        this.container.append($(this.el));
        this.container.trigger("create");
        return $(this.el);
    }
});
