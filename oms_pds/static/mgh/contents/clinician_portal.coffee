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
      .attr "y", (d, i) => @height - 50
      .style "color", '#1A2F46'
      .style "font-weight", 200
      .text (d) => @name


participantHtml = (participant) ->
  html = '<div class="patient" id=' + participant.uid + '>' + '<h3 class="patient-name">' + participant.uid + '</h3>'
  aspects = (k for k in Object.keys(participant) when k != 'uid')
  for aspect in aspects
    html += '<svg id="' + aspect + '-' + participant.uid + '"></svg>'
  html += '</div>'

for participant in participant_data
  $("#patients").append participantHtml(participant)


aspects = ['goal', 'activity', 'social', 'focus', 'glucose', 'meds', 'sleep']

colors = d3.scale.ordinal()
  .domain(['good', 'medium', 'bad'])
  .range(['#3FE963', '#F5C700', '#F34D4F'])

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
