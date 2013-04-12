window.SurveyQuestion = Backbone.Model.extend({
    urlRoot: SURVEY_QUESTION_API_URL
});

window.SurveyQuestionCollection = Backbone.Collection.extend({
    model: SurveyQuestion,
    urlRoot: SURVEY_QUESTION_API_URL,

    initialize: function (models, options) {
        this.options = options;
    },

    fetch: function (options) {
        options || (options = {});
        options.data || (options.data = {});
        this.options || (this.options = { survey: GET("survey") })
        filterMapping = { "survey": this.options.survey }
        options.data = _.extend(options.data, filterMapping);
        // Note: we probably want to make this configurable, for the cases where we might be hosting survey questions on the PDS (??)
        options.dataType = "jsonp";
  
        return Backbone.Collection.prototype.fetch.call(this,options);
    }
});

window.SurveyQuestionDropDownView = Backbone.View.extend({
    el: "<div data-role='fieldcontain'>",

    initialize: function (surveyQuestion) {
        _.bindAll(this, "render", "saveAnswer");

        this.surveyQuestion = surveyQuestion;
        this.answerKey = surveyQuestion[0].attributes.survey_question.answer_key;
        this.answerListCollection = new AnswerListCollection([], { key: this.answerKey });
        this.answerListCollection.fetch();
        
        if (typeof(android) !== "undefined" && android.registerQuestion) {
            android.registerQuestion(this.answerKey);
        }
    },

    render: function () {
        var me = this;
        var el = $(this.el);
        var question = this.surveyQuestion[0].attributes.survey_question.question;
        el.append("<label for='" + this.answerKey + "'>" + question + "</label>");

        var answers = $("<select id='" + this.answerKey + "'>");
        $.each(this.surveyQuestion, function () { answers.append($("<option value='" + this.attributes.survey_answer.value + "'>" + this.attributes.survey_answer.description + "</option>")); });
       
        el.append(answers);
        answers.selectmenu();
        answers.selectmenu().change(me.saveAnswer);
        answers.selectmenu("refresh");
        return el;
    },

    saveAnswer: function () {
        var answerModel = this.answerListCollection.at(0);
        answerModel || (answerModel = new AnswerList({ key: this.answerKey, value: [] }));
        var mostRecentAnswerTime = (answerModel.get("value").length > 0)? answerModel.get("value")[0].time : 0;
        var now = (new Date).getTime() / 1000;
        var answer = $("#" + this.answerKey).val();

        this.selectedAnswer = answer;

        if (now > mostRecentAnswerTime + 3600) {
            answerModel.get("value").unshift({ time: now, value: answer });
        } else {
            answerModel.get("value")[0].value = answer;
        }
        
        answerModel.save();

        if (typeof(android) !== "undefined" && android.markQuestionAsAnswered) {
            android.markQuestionAsAnswered(this.answerKey);
        }
    },
});

window.SurveyView = Backbone.View.extend({
    el: "<div>",

    initialize: function (surveyId, $el) {
        _.bindAll(this, "render");

        this.surveyQuestionCollection = new SurveyQuestionCollection([], { "survey": surveyId });
        this.surveyQuestionCollection.bind("reset", this.render);
        this.surveyQuestionCollection.fetch();
        this.$el = $el;
    },

    render: function() {
        surveyQuestions = this.surveyQuestionCollection.groupBy(function (q) { return q.attributes.survey_question.id; });
        var el = (this.$el)? this.$el : $(this.el);
        for (question in surveyQuestions) {
            var questionView = new SurveyQuestionDropDownView(surveyQuestions[question]);
            el.append(questionView.render());
        }

        return el;
    }
});
