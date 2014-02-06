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
    
    bindAll: function () {  
         _.bindAll(this, "render", "saveAnswer", "selectedValue");
    },

    initialize: function (surveyQuestion) {
        this.bindAll();

        this.surveyQuestion = surveyQuestion;
        this.questionText = surveyQuestion[0].attributes.survey_question.question;
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
        el.append("<label for='" + this.answerKey + "'>" + this.questionText + "</label>");

        var answers = $("<select id='" + this.answerKey + "'>");
        answers.append($("<option value='' data-placeholder='true'>Choose one...</option>"));
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
        var answer = this.selectedValue();

        if (now > mostRecentAnswerTime + 3600) {
            answerModel.get("value").unshift({ time: now, value: answer });
        } else {
            answerModel.get("value")[0].value = answer;
        }
        
        var me = this;

        // NOTE: we want to mark the question as answered regardless of if the save succeeds
        // We've disabled the back button in the android app, so we need to give control back to the user
        // even if their connection (or our server) is having issues.
        answerModel.save({}, { 
            success: function () {
                if (typeof(android) !== "undefined" && android.markQuestionAsAnswered) {
                    android.markQuestionAsAnswered(me.answerKey);
                }
            },
            error: function () {
                if (typeof(android) !== "undefined" && android.markQuestionAsAnswered) {
                    android.markQuestionAsAnswered(me.answerKey);
                }
            }
        });
    },

    selectedValue: function () {
        return $("#" + this.answerKey).val();
    }
});

window.SurveyQuestionStarView = SurveyQuestionDropDownView.extend({
    el: "<div class='answer-rating'>",
    selectedRating: 0,

    bindAll: function () {
        _.bindAll(this, "render", "appendStar", "selectedValue");
    },

    render: function () {
        var el = $(this.el);
        el.empty();
        el.append("<h2>" + this.questionText + "</h2>");
        var yellow = this.selectedRating;

        for (i = 1; i <= yellow; i++) {
            this.appendStar(i, "/static/img/star_3.png");
        }
        for (i = Math.floor(yellow + 1); i <= 5; i++) {
            this.appendStar(i, "/static/img/star_1.png");
        }

        return el;
    },

    appendStar: function (value, imgSrc) {
        var me = this;
        $(this.el).append($("<img src='"+imgSrc+"' />").click(function () { me.selectedRating = value; me.saveAnswer(); me.render() }));
    },

    selectedValue: function () {
        return this.selectedRating;
    }
});

window.SurveyQuestionView = function (surveyQuestion) {
    switch (surveyQuestion[0].attributes.survey_question.answer_type) {
        case 1:
            surveyQuestionView = new SurveyQuestionStarView(surveyQuestions[question]);
            break;
        default:
            surveyQuestionView = new SurveyQuestionDropDownView(surveyQuestions[question]);
            break;
    }

    return surveyQuestionView;
}

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
            var questionView = new SurveyQuestionView(surveyQuestions[question]);
            el.append(questionView.render());
        }

        return el;
    }
});
