class BarChart
  constructor: (data, width, height) ->
    @margin = {'top': 20, 'right': 20, 'bottom': 30, 'left': 50}
    @width = width - @margin.left - @margin.right
    @height = height - @margin.top - @margin.bottom

    console.log "data:", data

    # don't change these
    @userData = @processData data['user']
    @groupData = @processData data['group']

    @cutoff = new Date dayCutoff
    @group = false

    #@data = @aggregate @userData
    @data = @userData
    console.log "current data:", @data

    @updateXScale()

    @y = d3.scale.linear()
      .domain([0, 100])
      .range([@height, 0])


  getDateFormat: () ->
      if @cutoff == monthCutoff
        d3.time.format '%b %d'
      else if @cutoff == weekCutoff
        d3.time.format '%b %d'
      else if @cutoff == dayCutoff
        d3.time.format '%b %d, %H:00'
      else
        d3.time.format '%b %d'


  # does initial data processing
  processData: (data) ->
    newData = []
    for d in data
      d['time'] = new Date (d['time'] * 1000)
      d['score'] = d['score']
      newData.push(d)
    newData

  updateXScale: () ->
    parseDate = @getDateFormat()

    if @cutoff?
      @x = d3.scale.ordinal()
        .domain([@cutoff, d3.max(@data, (d) -> d.time)])
        .rangeRoundBands([0, @width], 0.15)
    else
      @x = d3.scale.ordinal()
        .domain @data.map (d) -> d.time
        .rangeRoundBands([0, @width], 0.15)


  aggregate: (data) ->
    parseDate = @getDateFormat()
    console.log "data to agg:", data
    data = d3.nest()
      .key (d) -> parseDate d.time
      .rollup (d) -> d3.mean(d, (g) -> g.score)
      .entries data

    for d in data
      d['x'] = d.key
      d['y'] = d.values
      delete d.key
      delete d.values
    return data


  showGroups: () ->
    @group = !@group

    # data update
    if @group
      userData = @aggregate (d for d in @userData where d.time >= cutoff)
      userData = userData.sort (d) -> d.x
      groupData = @aggregate (d for d in @groupData where d.time >= cutoff)
      groupData = groupData.sort (d) -> d.x

      data = []
      for d, i in userData
        obj = {x: d.x,
        data: [{name: "user", value: d.y},
        {name: "group", value: groupData[i].y}]}
        data.push obj
      @data = data
    else
      userData = @aggregate (d for d in @userData where d.time >= cutoff)
      @data = userData

    parseDate = @getDateFormat()

    @updateXScale()

    # inner x axis
    barTypes = ['user', 'group']
    @x1 = d3.scale.ordinal()
      .domain(barTypes)
      .rangeRoundBands([0, @x.rangeBand()]);

    @chart.selectAll('g.x.axis')
      .transition()
      .duration 500
      .style "opacity", 0
      .remove();

    @renderXAxis()

    @chartBody.selectAll('.user')
      .transition()
      .duration 500
      .attr "y", @height - 0.5
      .attr "height", 0
      .remove()

    bars = @chartBody.selectAll('.time')
      .data(@data)
      .enter().append("g")
      .attr "class", "g"
      .attr "transform", (d) -> "translate(" + @x(parseDate d.x) + ",0)"

    bars.selectAll("rect")
      .data (d) -> d.data
      .enter().append("rect")
      .attr "width", @x1.rangeBand()
      .attr "x", (d) -> @x1 d.name
      .attr "height", 0
      .attr "y", @height - 0.5
      #.attr "fill" (d) -> @colors[d.name]
      .attr "class", 'user'
      .transition()
      .delay 100
      .duration 1000
      .attr "y", (d) -> @y d.value
      .attr "height", (d) -> @height - @y(d.value)


  updateCutoff: (cutoff) ->
    @cutoff = cutoff
    @data = @aggregate @userData
    label = "user"

    parseDate = @getDateFormat()

    @updateXScale()

    @chart.selectAll('g.x.axis')
      .transition()
      .duration 500
      .style "opacity", 0
      .remove()

    @renderXAxis()

    @chartBody.selectAll(".bar")
      .data(@data).enter()
      .append "rect"
      .attr "width", @x.rangeband()
      .attr "x", (d) -> @x d.x
      .attr "y", (d) -> @height - 0.5
      # color here
      .attr "class", label
      .transition()
      .delay 100
      .duration 1000
      .attr "y", (d) -> @y d.y
      .attr "height", (d) -> @height - @y(d.y)


  renderXAxis: () ->
    parseDate = @getDateFormat()

    @xAxis = d3.svg.axis()
      .scale @x
      .orient "bottom"
      .tickSize 0
      .ticks 3

    @chart.append('g')
      .style "opacity", 0
      .attr "class", "x axis"
      .attr "transform", "translate(" + @height + ")"
      .attr('font-size', '13pt')
      .attr('font-family', 'Roboto Light')
      .transition()
      .duration(1000)
      .style('opacity', 100)
      .call @xAxis


  render: (id) ->
    @chart = d3.select(id)
      .append "svg"
      .attr "class", "history-chart"
      .attr "width", @width + @margin.left + @margin.right
      .attr "height", @height + @margin.top + @margin.bottom
      .append 'g'
      .attr "transform", "translate(" + @margin.left + "," + @margin.top + ")"

    @chartBody = @chart.append("g")
      .attr "width", @width
      .attr "height", @height

    @updateXScale()

    @chart.selectAll('g.x.axis')
      .transition()
      .duration 500
      .style "opacity", 0
      .remove()

    @renderXAxis()

    @chartBody.selectAll(".bar")
      .data(@data)
      .enter()
      .append "rect"
      .attr "width", @x.rangeBand()
      .attr "x", (d) => @x(d.time)
      .attr "y", (d) => @height - 0.5
      # color here
      .attr "class", "user"
      .transition()
      .delay 100
      .duration 1000
      .attr "y", (d) => @y d.score
      .attr "height", (d) => @height - @y(d.score)


data = {user: userHistory['sleep'], group: groupHistory['sleep']}

sleepChart = new BarChart data, 400, 300
sleepChart.render('#chart')
