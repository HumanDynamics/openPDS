window.AnswerListMap = Backbone.View.extend({
    el: "#answerListMapContainer",
    
    initialize: function (answerKey, center) {
        _.bindAll(this, "render", "renderPlaces");
        
        this.center = center;
        this.render();
        this.answerLists = new AnswerListCollection([],{ "key": answerKey });
        this.answerLists.bind("reset", this.renderPlaces);
        this.answerLists.fetch();
    },
    
    render: function () {
        this.map = new OpenLayers.Map({ 
            div: "answerListMapContainer",
            projection: new OpenLayers.Projection("EPSG:900913"),
            displayProjection: new OpenLayers.Projection("EPSG:4326"),
            numZoomLevels: 18,
            tileManager: new OpenLayers.TileManager(),
//            fractionalZoom: true
        });

        this.map.addControls([
            new OpenLayers.Control.TouchNavigation({dragPanOption: { enableKinetic: true}}),
        ]);  
        var osm = new OpenLayers.Layer.OSM();
        this.map.addLayers([osm]);
        this.updateSize();
    },
    
    addKeyRadioButton: function (ext, boxes, entry, j, keyFields) {
        var bounds = OpenLayers.Bounds.fromArray(ext, true);
        bounds = bounds.transform(this.map.displayProjection, this.map.getProjectionObject());
        var box = new OpenLayers.Feature.Vector(bounds.toGeometry());
        boxes.addFeatures([box]);
        this.entryBounds[j] = bounds.clone();
        var me = this;
        var radioButton = $("<label for='place"+j+"'>"+entry["key"]+"</label><input type='radio' data-mini='true' name='place' value='"+j+"' id='place"+j+"' />");
        keyFields.controlgroup("container").append(radioButton.click(
            function () {
                me.map.zoomToExtent(me.entryBounds[this.value]);
             }
        ));
        $(radioButton[1]).checkboxradio();
    },

    renderPlaces: function () {
        var entries = this.answerLists.at(0).get("value");
        var boxes  = new OpenLayers.Layer.Vector( "Boxes" );
        var pointsLayer = new OpenLayers.Layer.Vector("Points");


        var minLat = minLong = Number.MAX_VALUE;
        var maxLat = maxLong = -Number.MAX_VALUE;
        var footer = $("#footer");//$("<div data-role='footer'></div>");
        var keyFields = $("<fieldset data-role='controlgroup' data-type='horizontal' data-mini='true'></fieldset>").controlgroup();
        footer.append(keyFields);
        this.entryBounds = [];
        var j = 0;
        for (i in entries) {
            var entry = entries[i];
            var ext = entry["bounds"];
            if (ext) {
                if (typeof ext[0] !== "number") {
                    for (b in ext) {
                        r = ext[b];

                        minLat = Math.min(minLat, r[0]);
                        maxLat = Math.max(maxLat, r[2]);
                        minLong = Math.min(minLong, r[1]);
                        maxLong = Math.max(maxLong, r[3]);
                        this.addKeyRadioButton(r, boxes, entry, j, keyFields); 
                        j++;
                    }
                } else {
                    minLat = Math.min(minLat, ext[0]);
                    maxLat = Math.max(maxLat, ext[2]);
                    minLong = Math.min(minLong, ext[1]);
                    maxLong = Math.max(maxLong, ext[3]);                            
                    this.addKeyRadioButton(ext, boxes, entry, j, keyFields);
                    j++;
                }
            }

            footer.appendTo("#pageDiv").toolbar({ position: "fixed" });

            points = entry["points"];

            if (points) {
                for (pointIndex in points) {
                    var point = points[pointIndex];

                    minLat = Math.min(minLat, point[0]);
                    maxLat = Math.max(maxLat, point[0]);
                    minLong = Math.min(minLong, point[1]);
                    maxLong = Math.max(maxLong, point[1]);

                    pointGeometry = new OpenLayers.Geometry.Point(point[1], point[0]);
                    pointGeometry = pointGeometry.transform(this.map.displayProjection, this.map.getProjectionObject());
                    pointVector = new OpenLayers.Feature.Vector(pointGeometry);
                    pointsLayer.addFeatures([pointVector]);
                }
            }
        }
        this.map.addLayers([boxes,pointsLayer]);
        
        if (minLong < Number.MAX_VALUE && maxLong > -Number.MAX_VALUE && !this.center) {
            bounds = OpenLayers.Bounds.fromArray([minLong, minLat, maxLong, maxLat]);
            bounds.transform(this.map.displayProjection, this.map.getProjectionObject());
            this.map.zoomToExtent(bounds);
        } else if (this.center) {
            //center = new OpenLayers.Geometry.Point(this.center[1], this.center[0]);
            center = new OpenLayers.LonLat(this.center[1], this.center[0]);
            center.transform(this.map.displayProjection, this.map.getProjectionObject());
            this.map.setCenter(center, 18);
            //this.map.setCenter(new OpenLayers.LonLat(this.center[1], this.center[0]), 10);
        }
        this.updateSize();
        //setTimeout(this.updateSize, 1000);
    },
    
    zoomIn: function () {
        if (this.map) {
            this.map.zoomIn();
        }
    },
    
    zoomOut: function () {
        if (this.map) {
            this.map.zoomOut();
        }
    },
    
    updateSize: function () {
        var navbar= $("div[data-role='navbar']:visible"),
        content = $("div[data-role='content']:visible:visible"),
        footer = $("div[data-role='footer']:visible"),
        viewHeight = $(window).height(),
        contentHeight = viewHeight - navbar.outerHeight() - footer.outerHeight();
   
//        console.log("view, content, navbar, footer, outer"+viewHeight+","+contentHeight+","+navbar.outerHeight()+","+footer.outerHeight()+","+content.outerHeight());
         
        if (content.outerHeight() !== contentHeight) {
            content.height(contentHeight);
        }
    
        if (this.map && this.map instanceof OpenLayers.Map) {
            this.map.updateSize();
        }
    }
    
});
