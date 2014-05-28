/**
 * jQuery SPARQL
 * 
 * Provides an idiomatic jQuery-like interface to SPARQL endpoints.
 * Queries are built through method-chaining, before being compiled into a
 * string query which can be sent to the endpoint.
 *
 * $.sparql("http://www.example.com/sparql/").prefix("foaf","http://xmlns.com/0.1/foaf/")
 *  .select()
 *  .where("?p", "a", "foaf:Person")
 *        .where("foaf:name", "?name")
 *        .where("foaf:homepage", "?page")
 *  .orderby("?name")
 *  .distinct()
 *  .execute(cbfunc);
 */
(function($){
  
  $.yql = function(query, callback) {
    var url = "http://query.yahooapis.com/v1/public/yql?format=json&q=" + $.URLEncode(query);
    $.ajax({ url: url, dataType: "jsonp", success: callback });
  };

  var URI = function(uri) {
    this.uri = uri;
  };
  
  var Query = function(endpoint, options, parentQuery) {
    this.config = {
      "endpoint" : endpoint,
      "method" : "GET",
      "output" : "json"
    };
    
    this._parentQuery = parentQuery;
    this.queryType = "SELECT";
    this.prefixes = [];
    this.defaultGraphs = [];
    this.namedGraphs = [];
    this.variables = [];
    this.patterns = [];
    this.filters = [];
    this.combiner = "";
    this.orders = [];
    this.limitCount = -1;
    this.offsetCount = 0;
    this._prevSubj = null;
    this._prevProp = null;
    this._storedQuery = "";
    
    // Override the defaults with anything interesting
    if (options) $.extend(this.config, options);
  };
  
  Query.prototype.end = function() {
    return this._parentQuery;
  };
  
  Query.prototype.query = function(qstring) {
    this._storedQuery = qstring;
    return this;
  };
  
  Query.prototype.execute = function(callback) {
    var endpoint = this.config.endpoint;
    var method = this.config.method;
    var output = this.config.output;
    var queryString = this._storedQuery;

    var _clean = function(val) {
      if(val.type == "literal") {
        return val.value;
      }
      else if(val.type == "uri") {
        return new URI(val.value);
      }
      else {
        return val.value;
      }
    };
    
    var _preproc = function(data) {
      var results = data.query.results.sparql.result;
      var cleaned_results = [];
      for(var r in results) {
        var result = results[r];
        var cleaned_obj = {};
        for(var k in result) {
          cleaned_obj[k] = _clean(result[k]);
        }
        cleaned_results.push(cleaned_obj);
      }
      callback(cleaned_results);
    };
    
    if (queryString == "") queryString = this.serialiseQuery();
    if(method == "GET") {
      var yqlQuery = 'use "http://triplr.org/sparyql/sparql.xml" as sparql; select * from sparql where query="' + queryString + '" and service="' + endpoint + '"';
      $.yql(yqlQuery, _preproc);
      
      return this;
    }
    throw "Only GET method supported at this time.";
  };
  
  Query.prototype.serialiseQuery = function() {
    var queryString = [];
    
    // Prefixes
    for(var i = 0; i < this.prefixes.length; i++) {
      var pfx = this.prefixes[i];
      queryString.push( "PREFIX " + pfx.prefix + ": <" + pfx.uri + ">");
    }
    
    // Type and projection 
    queryString.push(this.queryType);
    if(this.combiner != "") {
      queryString.push(this.combiner);
    }
    if(this.queryType == "SELECT" && this.variables.length == 0) {
      queryString.push("*"); // No variables is seen as an implicit projection over ALL variables
    }
    else {
      for(var i = 0; i < this.variables.length; i++) {
        var v = this.variables[i];
        queryString.push(v);
      }
    }
    
    // Add the default graphs
    for(var i = 0; i < this.defaultGraphs.length; i++) {
      var defaultGraph = this.defaultGraphs[i];
      queryString.push("FROM <" + defaultGraph + ">");
    }
    
    // Add the named graphs
    for(var i = 0; i < this.namedGraphs.length; i++) {
      var namedGrph = this.namedGraphs[i];
      queryString.push("FROM NAMED <" + namedGrph + ">");
    }
    
    // Start WHERE block
    queryString.push("WHERE {");
    
    // Basic triple patterns and more exotic blocks
    for(var i = 0; i < this.patterns.length; i++) {
      var pat = this.patterns[i];
      
      // Basic triple
      if(pat._sort == "triple") {
        queryString.push(pat.s + " " + pat.p + " " + pat.o + ".");
      }
      // Optionals
      else if(pat._sort == "optional") {
        queryString.push("OPTIONAL");
        queryString.push(pat.subquery.serialiseBlock());
      }
      // Graph blocks
      else if(pat._sort == "graph") {
        queryString.push("GRAPH");
        queryString.push(pat.graphName);
        queryString.push(pat.subquery.serialiseBlock());
      }
      // Service blocks
      else if (pat._sort == "service") {
        queryString.push("SERVICE");
        queryString.push("<" + pat.serviceEndpoint + ">");
        queryString.push(pat.subquery.serialiseBlock());
      }
      // Just blocks
      else if(pat._sort == "block") {
        queryString.push(pat.subquery.serialiseBlock());
      }
    }
    
    // Filters
    for(var i = 0; i < this.filters.length; i++) {
      var flt = this.filters[i];
      queryString.push("FILTER ( " + flt + " )");
    }
    
    // End WHERE block
    queryString.push("}");
    
    if(this.orders.length > 0) {
      queryString.push("ORDER BY");
      for(var i = 0; i < this.orders.length; i++) {
        var odr = this.orders[i];
        queryString.push(odr);
      }
    }
    
    if(this.limitCount > -1) {
      queryString.push("LIMIT " + this.limitCount);
    }
    
    if(this.offsetCount > 0) {
      queryString.push("OFFSET " + this.offsetCount);
    }
    
    return queryString.join(" ");
  };
  
  Query.prototype.serialiseBlock = function() {
    var queryString = [];
    
    // Start block
    queryString.push("{");
    
    // Basic triple patterns and more exotic blocks
    for(var i = 0; i < this.patterns.length; i++) {
      var pat = this.patterns[i];
      
      // Basic triple
      if(pat._sort == "triple") {
        queryString.push(pat.s + " " + pat.p + " " + pat.o + ".");
      }
      // Optionals
      else if(pat._sort == "optional") {
        queryString.push("OPTIONAL");
        queryString.push(pat.subquery.serialiseBlock());
      }
      // Graph blocks
      else if(pat._sort == "graph") {
        queryString.push("GRAPH");
        queryString.push(pat.graphName);
        queryString.push(pat.subquery.serialiseBlock());
      }
      // Service blocks
      else if (pat._sort == "service") {
        queryString.push("SERVICE");
        queryString.push("<" + pat.serviceEndpoint + ">");
        queryString.push(pat.subquery.serialiseBlock());
      }
      // Just blocks
      else if(pat._sort == "block") {
        queryString.push(pat.subquery.serialiseBlock());
      }
    }
    
    // Filters
    for(var i = 0; i < this.filters.length; i++) {
      var flt = this.filters[i];
      queryString.push("FILTER ( " + flt + " )");
    }
    
    // End block
    queryString.push("} .");
    
    return queryString.join(" ");
    
  };
  
  Query.prototype.distinct = function() {
    this.combiner = "DISTINCT";
    return this;
  };
  
  Query.prototype.reduced = function() {
    this.combiner = "REDUCED";
    return this;
  };
  
  Query.prototype.select = function(variables) {
    this.queryType = "SELECT";
    if (variables) this.variables = variables;
    return this;
  };
  
  Query.prototype.describe = function(variables) {
    this.queryType = "DESCRIBE";
    if (variables) this.variables = variables;
    return this;
  };
  
  Query.prototype.prefix = function(prefix, uri) {
    this.prefixes.push({ "prefix" : prefix, "uri" : uri});
    return this;
  };
  
  Query.prototype.from = function(graph, isNamed) {
    if(isNamed) {
      this.namedGraphs.push(graph);
    }
    else {
      this.defaultGraphs.push(graph);
    }
    return this;
  };
  
  Query.prototype.where = function(subj, prop, obj) {
    if (!obj && !prop) {
      // We're in a subj-prop repeating section, use previous subj and prop
      return this.where(this._prevSubj, this._prevProp, subj);
    }
    else if (!obj) {
      // We're in a subj repeating section, use previous subj
      this._prevProp = subj;
      return this.where(this._prevSubj, subj, prop);
    }
    else {
      // We have a full triple
      this._prevSubj = subj;
      this._prevProp = prop;
      this.patterns.push({ "_sort" : "triple", "s" : subj, "p" : prop, "o" : obj });
      return this;
    }
  };
  
  Query.prototype.filter = function(filter) {
    this.filters.push(filter);
    return this;
  };
  
  Query.prototype.orderby = function(order) {
    this.orders.push(order);
    return this;
  };
  
  Query.prototype.limit = function(limit) {
    this.limitCount = limit;
    return this;
  };
  
  Query.prototype.offset = function(offset) {
    this.offsetCount = offset;
    return this;
  };
  
  Query.prototype.optional = function() {
    var opt = new Query(this.config.endpoint, this.config, this);
    this.patterns.push({ "_sort" : "optional", "subquery" : opt });
    return opt;
  };
  
  Query.prototype.graph = function(name) {
    var grph = new Query(this.config.endpoint, this.config, this);
    this.patterns.push({ "_sort" : "graph", "graphName" : name, "subquery" : grph });
    return grph;
  };

  Query.prototype.service = function(endpoint) {
    var srvc = new Query(this.config.endpoint, this.config, this);
    this.patterns.push({ "_sort" : "service", "serviceEndpoint" : endpoint, "subquery" : srvc });
    return srvc;
  };
  
  Query.prototype.block = function() {
    var blk = new Query(this.config.endpoint, this.config, this);
    this.patterns.push({ "_sort" : "block", "subquery" : blk });
    return blk;
  };
  
  $.sparql = function(endpoint, options) {
    return new Query(endpoint, options);
  };
  
})(jQuery);
