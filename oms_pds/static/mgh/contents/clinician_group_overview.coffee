class StackedChart
  constructor: (data, colors, width, height) ->
    @colors = colors
    @margin = {'top': 10, 'right': 30, 'bottom': 50, 'left': 0}
    @width = width - @margin.left - @margin.right
    @height = height - @margin.top - @margin.bottom
    @formatPercent = (d) -> d * 100
    @parseDate = d3.time.format('%m/%d/%y').parse
    @data = data

    console.log "raw data:"
    console.log data

    for d in @data
      d['date'] = @parseDate(d['date'])

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

    console.log "stacked:"
    console.log @statuses

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
    @chart = d3.select(id)
      .append "svg"
      .attr "class", "agg-chart"
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


class Pie
  constructor: (data, name, colors, width) ->
    @data = data
    @colors = colors
    @width = width
    @height = width
    @radius = Math.min(@width, @height) / 2
    @name = name

    @arc = d3.svg.arc()
      .outerRadius @radius - 10
      .innerRadius @radius - 70

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
    console.log "rendering on id:" + id
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
      .attr "y", (d, i) => @height - 40
      .style "color", 'rgba(26, 47, 70, 0.80)'
      .style "font-weight", 200
      .text (d) => @name.replace('-', ' ')


participantHtml = (participant) ->
  name = uid_name_map[participant.uid]
  html = '<div class="patient" id=' + participant.uid + '>' + '<a href="/clinician/patients/' + participant.uid + '"><h3 class="patient-name">' + name + '</h3></a>'
  aspects = (k for k in Object.keys(participant) when k != 'uid')
  aspects = aspects.sort()
  for aspect in aspects
    html += '<svg class="pie" id="' + aspect + '-' + participant.uid + '"></svg>'
  html += '</div>'

for participant in participant_data
  $("#patients").append participantHtml(participant)

colors = d3.scale.ordinal()
  .domain(['bad', 'medium', 'good'])
  .range(['#F34D4F', '#F5C700', '#3FE963'])

margins = {'left': 10, 'right': 10}

for participant in participant_data
  aspects = (k for k in Object.keys(participant) when k != 'uid')
  for aspect in aspects
    id = "#" + aspect + "-" + participant.uid
    width = $('#patients').width() - margins.left - margins.right
    parent = '#' + participant.uid
    $(parent).css('margin-left', margins.left + "px")
    $('.patient-name').css('margin-left', margins.left + "px")
    chart_width = width / aspects.length
    $(id).width(chart_width)
    data = participant[aspect]
    pie = new Pie(data, aspect, colors, chart_width)
    pie.render(id)


stacked = new StackedChart(aggregate_data, colors, 700, 350)
stacked.render('#group-chart')
