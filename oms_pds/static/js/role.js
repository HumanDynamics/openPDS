$(function () {

// NOTE: we probably want to move these ajax setup operations into a more general file for inclusion
// by all admin interfaces
window.Role = Backbone.Model.extend({});

window.RoleCollection = Backbone.Collection.extend({
    model: Role,
    urlRoot: ROLE_API_URL,

    parse: function (data) {
	return data.objects;
    }
});

window.RoleView = Backbone.View.extend({
    tagName: "div",

    initialize: function () {
        this.model.on('change', this.render, this);
        this.model.on('destroy', this.remove, this);
    },
    
    render: function() {
        $(this.el).html(ich.roleTemplate(this.model.toJSON()));
        return this;
    },

    remove: function() { 
        $(this.el).remove();
    }
});

window.RolesApp = Backbone.View.extend({
    el: "#content",

    events: {
        "click .createRoleButton": "createRole",
        "click .deleteSelectedRolesButton": "deleteSelectedRoles"
    },

    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll', 'removeOne');
        this.roles = new RoleCollection();
        this.roles.bind('add', this.addOne);
        this.roles.bind('reset', this.addAll);
        this.roles.bind('remove', this.removeOne);
        this.roles.fetch();
    },

    addOne: function (role) {
        var view = new RoleView({model: role});
        $('#roles').append(view.render().el);
    },

    addAll: function() {
        this.roles.each(this.addOne);
    },

    removeOne: function (role) {
        role.destroy();
    },

    createRole: function () {
        var keyValue = $('#keyTextBox').val();
	var idsValue = $('#idsTextBox').val();
        if (keyValue && idsValue) {
            this.roles.create({
                key: keyValue,
                ids: idsValue.split(',')
            });
            $('#keyTextBox').val('');
            $('#idsTextBox').val('');
        }
    },
    
    deleteSelectedRoles: function () {
        var selected = this.$(".roleCheckBox:checked");
	var me = this;
        selected.each(function () { 
            var modelId = $(this).val();
            var model = me.roles.find(function (r) { return r.id.indexOf(modelId) != -1; });
            if (model) {
                me.roles.remove(model);
            }
        });
    }
});

window.app = new RolesApp();
});
