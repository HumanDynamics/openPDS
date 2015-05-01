class window.StackedChart
  constructor: (data, colors, label, width, height) ->
    @colors = colors
    @margin = {'top': 30, 'right': 30, 'bottom': 50, 'left': 0}
    @width = width - @margin.left - @margin.right
    @height = height - @margin.top - @margin.bottom
    @formatPercent = (d) -> d * 100
    @parseDate = d3.time.format('%m/%d/%y').parse
    @label = label
    @rawData = data

    #console.log "raw data:"
    #console.log data

    # circumvents the 'copying' problem
    @data = []
    for d in @rawData
      obj = {'date': @parseDate(d['date']), 'key': d.key, 'value': d.value}
      @data.push(obj)

    @dates = d3.extent @data, (d) -> d.date

    @data = d3.nest()
      .key (d) -> d['key']
      .entries(@data)

    @stack = d3.layout.stack()
      .offset "zero"
      .values (d) -> d.values
      .x (d) -> d.date
      .y (d) -> d.value

    @statuses = @stack @data

    #console.log "stacked:"
    #console.log @statuses

    @x = d3.time.scale()
      .domain @dates
      .range([0, @width])

    @y = d3.scale.linear()
      .range([@height, 0])

    @xAxis = d3.svg.axis()
      .scale @x
      .orient "bottom"
      .ticks d3.time.month
      .tickSize 0
      .tickFormat d3.time.format('%B')

    @yAxis = d3.svg.axis()
      .scale @y
      .orient 'right'
      .ticks 1
      .tickSize 0
      .tickFormat @formatPercent

    @area = d3.svg.area()
      .interpolate("cardinal")
      .x (d) => @x(d.date)
      .y0 (d) => @y(d.y0)
      .y1 (d) => @y(d.y0 + d.y)

  render: (id) ->
    @svg = d3.select(id)
      .append "svg"
      .attr "class", "agg-chart"

    @chart = @svg
      .attr "width", @width + @margin.left + @margin.right
      .attr "height", @height + @margin.top + @margin.bottom
      .append "g"
      .attr "transform", "translate(" + @margin.left + "," + @margin.top + ")"

    @chartBody = @chart.append("g")
      .attr "width", @width
      .attr "height", @height

    @status = @chartBody.selectAll('.status')
      .data(@statuses)
      .enter().append("g")
      .attr "class", "status"

    @status.append("path")
      .attr "class", "area"
      .attr "d", (d) => @area d.values
      .style "fill", (d) => @colors d.key

    @chart.append("g")
      .attr "class", "axis"
      .attr "transform", "translate(0," + (@height + 10) + ")"
      .style "fill", 'rgba(26, 47, 70, 0.80)'
      .call @xAxis
      .selectAll "text"
      .attr "y", "10px"

    @chart.append("g")
      .attr "class", "y-axis"
      .attr "transform", "translate(" + @width + ",0)"
      .style "fill", '#bcbcbc'
      .call @yAxis

    @svg.append("text")
      .attr "class", "group-overview-title"
      .attr "text-anchor", "left"
      .attr "y", (d, i) => @margin.top / 2
      .attr "x", (d, i) => @margin.left
      .style "color", 'rgba(26, 47, 70, 0.80)'
      .style "font-weight", 300
      .style "font-size", '1.2em'
      .text (d) => @label


class window.Pie
  constructor: (data, name, colors, width) ->
    @data = data
    @colors = colors
    @width = width
    @height = width
    @radius = Math.min(@width, @height) / 2
    @name = name

    @arc = d3.svg.arc()
      .outerRadius @radius - 10
      # .innerRadius @radius - 70

    @pie = d3.layout.pie()
      .sort null
      .value (d) -> d.score

    @tip = d3.tip()
      .attr "class", "d3-tip"
      .offset([-10, 0])
      .html (d) ->
        '<span>' + d.data.status + ': ' +
        Math.floor(d.data.score * 100) + '%</span>'

  render: (id) ->
    #console.log "rendering on id:" + id
    @svg = d3.select(id)
      .append("g")
      .attr("transform", "translate(" + @width / 2 + "," + @height / 2 + ")")

    @svg.call(@tip)

    @g = @svg.selectAll('.arc')
      .data @pie(@data)
      .enter().append("g")
      .attr "class", "arc"
      .on "mouseover", @tip.show
      .on "mouseout", @tip.hide

    @g.append("path")
      .attr "d", @arc
      .style "fill", (d) => @colors(d.data.status)

    @svg.append("text")
      .attr "class", "pietext"
      .attr "text-anchor", "middle"
      .attr "y", (d, i) => (@height / 2) + 20
      .style "color", 'rgba(26, 47, 70, 0.80)'
      .style "font-weight", 200
      .text (d) => @name.replace('-', ' ')


# patient pie charts

colors = d3.scale.ordinal()
  .domain(['bad', 'medium', 'good', 'No Data'])
  .range(['#F34D4F', '#F5C700', '#3FE963', '#E2E2E2'])

window.margins = {'left': 10, 'right': 10}

$('.patient').width($('#patients').width() / 2)

for participant in participant_data
  $('.patient-name').css('margin-left', margins.left + "px")

  chart_info = {
    'agg_scores': {'name': "Control + Intervention", 'id': '#aggChart-'},
    'intervention_scores': {'name': "Intervention", 'id': '#intChart-'},
    'control_scores': {'name': 'Control', 'id': '#conChart-'}}


  for t in ['agg_scores', 'intervention_scores', 'control_scores']
    # aggregate pie charts
    width = 200
    text_margin = 40;
    id = chart_info[t]['id'] + participant.uid
    width = $('#patients').width() - margins.left - margins.right
    chart_width = width / 4
    $(id).width(chart_width)
    $(id).height(chart_width + 20)
    data = participant[t]
    console.log data
    console.log id
    pie = new Pie(data, chart_info[t]['name'], colors, chart_width)
    pie.render(id)
    if t != 'agg_scores'
      $(id).hide()


  aspects = (k for k in Object.keys(participant.scores))
  for aspect in aspects
    id = "#" + aspect + "-" + participant.uid
    width = $('#patients').width() - margins.left - margins.right
    parent = '#' + participant.uid + '-categories'
    $(parent).css('margin-left', margins.left + "px")
    chart_width = (width / aspects.length) - 5
    $(id).width(chart_width)
    $(id).height(chart_width + 20)
    data = participant.scores[aspect]
    pie = new Pie(data, aspect, colors, chart_width)
    pie.render(id)
    $(parent).hide()



# group aggregate charts

gHeight = 300
gWidth = 750

for status in ['i', 'c']
  if status == 'i'
    label = "Intervention Arm:"
    $("#group-charts").append('<div flex class="group-chart" id="intervention-chart"></div>')
    window.iStacked = new StackedChart(aggregate_data['All Categories'][status], colors, label, gWidth, gHeight)
    window.iStacked.render('#intervention-chart')
  else if status == 'c'
    label = "Control Group:"
    $("#group-charts").append('<div flex class="group-chart" id="control-chart"></div>')
    window.cStacked = new StackedChart(aggregate_data['All Categories'][status], colors, label, gWidth, gHeight)
    window.cStacked.render('#control-chart')


# add dropdown items for aggregate data
for aspect in Object.keys(aggregate_data)
  $('#agg').append('<paper-item name="' + aspect + '">' + aspect + '</paper-item>')


window.changeAggCharts = (aspect) ->
  console.log aspect

  # remove charts
  $('#intervention-chart').fadeOut(500)
  $('#control-chart').fadeOut(500)
  $('#control-chart').remove()
  $('#intervention-chart').remove()

  # create new intervention and control charts
  $("#group-charts").append('<div flex class="group-chart" id="intervention-chart"></div>')
  $("#intervention-chart").hide()
  iData = aggregate_data[aspect]['i']
  console.log iData
  window.iStacked = new StackedChart(iData, colors, "Intervention Arm", gWidth, gHeight)
  window.iStacked.render('#intervention-chart')

  $("#group-charts").append('<div flex class="group-chart" id="control-chart"></div>')
  $("#control-chart").hide()
  window.cStacked = new StackedChart(aggregate_data[aspect]['c'], colors, "Control Group", gWidth, gHeight)
  window.cStacked.render('#control-chart')

  # fade them in
  $("#intervention-chart").fadeIn(500)
  $("#control-chart").fadeIn(500)
