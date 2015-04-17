class Pie
  constructor: (data, name, colors, width) ->
    @data = data
    @colors = colors
    @width = width
    @height = width
    @radius = Math.min(@width, @height) / 2;
    @name = name

    @arc = d3.svg.arc()
      .outerRadius @radius - 10
      .innerRadius @radius - 70

    @pie = d3.layout.pie()
      .sort null
      .value (d) -> d.score

  render: (id) ->
    @svg = d3.select(id)
      .append("g")
      .attr("transform", "translate(" + @width / 2 + "," + @height / 2 + ")");

    @g = @svg.selectAll('.arc')
      .data @pie(@data)
      .enter().append("g")
      .attr "class", "arc"

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


participantHtml = (uid) ->
  '<div class="patient" id=' + uid + '>' +
    '<h4 class="patient-name">' + uid + '</h4>' +
    '<svg id="goal-' + uid + '"></svg>' +
    '<svg id="activity-' + uid + '"></svg>' +
    '<svg id="social-' + uid + '"></svg>' +
    '<svg id="focus-' + uid + '"></svg>' +
    '<svg id="glucose-' + uid + '"></svg>' +
    '<svg id="meds-' + uid + '"></svg>' +
    '<svg id="sleep-' + uid + '"></svg>' +
  '</div>'


for participant in participant_data
  $("#patients").append participantHtml(participant.uid)


aspects = ['goal', 'activity', 'social', 'focus', 'glucose', 'meds', 'sleep']

colors = d3.scale.ordinal()
  .domain(['good', 'medium', 'bad'])
  .range(['#3FE963', '#F5C700', '#F34D4F'])

margins = {'left': 10, 'right': 10}

for participant in participant_data
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
