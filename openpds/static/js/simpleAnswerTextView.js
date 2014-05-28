window.SimpleAnswerTextView = Backbone.View.extend({
    el: "<div></div>",

    initialize: function (answerKey) {
        _.bindAll(this, "render", "populateAnswerData");

        this.answerKey = answerKey;

        this.answerCollection = new AnswerCollection([], { "key": this.answerKey });
        this.answerCollection.bind("reset", this.populateAnswerData);
        this.answerCollection.fetch();
        this.renderCalled = false;
        this.answer = null;
    },

    render: function() {
        this.renderCalled = true;
        if (this.answer) {
            for (var i in this.answer) {
                $(this.el).append("<div>" + i + ": " + this.answer[i] + "</div>");
            }
        }

        return $(this.el);
    },

    populateAnswerData: function () {
        this.answer = (this.answerCollection && this.answerCollection.length > 0) ? this.answerCollection.at(0).get("value") : {};
        if (this.renderCalled) {
            this.render();
        }
    }
});
