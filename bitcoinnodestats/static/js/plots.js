// Set the dimensions of the canvas / graph
var margin = {top: 30, right: 20, bottom: 30, left: 50},
    width = 800 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

// Parse the date / time
var parseDate = d3.time.format("%Y-%m-%d %H:%M:%S").parse;
var bisectDate = d3.bisector(function(d) { return d.datetime; }).left;

// Set the ranges
var x = d3.time.scale().range([0, width]);
var y = d3.scale.linear().range([height, 0]);

// Define the axes
var xAxis = d3.svg.axis().scale(x)
    .orient("bottom").ticks(10);

var yAxis = d3.svg.axis().scale(y)
    .orient("left").ticks(10);

// Define the line
var valueline = d3.svg.line()
    .x(function(d) { return x(d.datetime); })
    .y(function(d) { return y(d.sent_mb); });

// Adds the svg canvas
var svg = d3.select("body").select("#data_usage_plot svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");


// Get the data
d3.json("/static/media/data_usage.json", function(data) {
    data.forEach(function(d) {
        d.datetime = parseDate(d.datetime);
    });

    // Scale the range of the data
    x.domain(d3.extent(data, function(d) { return d.datetime; }));
    y.domain([0, d3.max(data, function(d) { return d.sent_mb; })]);

    // Add the valueline path.
    svg.append("path")
        .attr("class", "line")
        .attr("d", valueline(data));

    // Append marker
    svg.selectAll(".dot")
      .data(data)
      .enter().append("circle")
      .attr("class", "dot")
      .attr("r", 2)
      .attr("cx", function(d) { return x(d.datetime); })
      .attr("cy", function(d) { return y(d.sent_mb); })
      .style("fill", "white")
      .style("stroke", "blue");

      // append the rectangle to capture mouse               // **********
    svg.append("rect")                                     // **********
        .attr("width", width)                              // **********
        .attr("height", height)                            // **********
        .style("fill", "none")                             // **********
        .style("pointer-events", "all")                    // **********
        .on("mouseover", function() { focus.style("display", null); })
        .on("mouseout", function() { focus.style("display", "none"); })
        .on("mousemove", mousemove);                       // **********

    var focus = svg.append("g")                                // **********
        .style("display", "none");

    // append the circle at the intersection               // **********
    focus.append("circle")                                 // **********
        .attr("class", "y")                                // **********
        .style("fill", "none")
        .style("stroke-width", 3)
        .style("stroke", "blue")                           // **********
        .attr("r", 5);

    // place the value at the intersection
    focus.append("text")
        .attr("class", "y1")
        .style("stroke", "white")
        .style("stroke-width", "3.5px")
        .style("opacity", 0.8)
        .attr("dx", 8)
        .attr("dy", "-.3em");

    focus.append("text")
        .attr("class", "y2")
        .attr("dx", 8)
        .attr("dy", "-.3em");

    // place the date at the intersection
    focus.append("text")
        .attr("class", "y3")
        .style("stroke", "white")
        .style("stroke-width", "3.5px")
        .style("opacity", 0.8)
        .attr("dx", 8)
        .attr("dy", "1em");

    focus.append("text")
        .attr("class", "y4")
        .attr("dx", 8)
        .attr("dy", "1em");

    function mousemove() {
        var x0 = x.invert(d3.mouse(this)[0]),              // **********
            i = bisectDate(data, x0, 1),                   // **********
            d0 = data[i - 1],                              // **********
            d1 = data[i],                                  // **********
            d = x0 - d0.date > d1.date - x0 ? d1 : d0;     // **********

        focus.select("circle.y")                           // **********
            .attr("transform",                             // **********
                  "translate(" + x(d.datetime) + "," +         // **********
                                 y(d.sent_mb) + ")");        // **********

        var formatDate = d3.time.format("%d-%b %H:%M");

        var tooltip_x = x(d.datetime) + 15;
        var tooltip_y = y(d.sent_mb) + 30;
        var translate_str = "translate(" + tooltip_x + "," + tooltip_y + ")";

        focus.select("text.y1")
            .attr("transform", translate_str)
            .text(Math.round(d.sent_mb));

        focus.select("text.y2")
            .attr("transform", translate_str)
            .text(Math.round(d.sent_mb));

        focus.select("text.y3")
            .attr("transform", translate_str)
            .text(formatDate(d.datetime));

        focus.select("text.y4")
            .attr("transform", translate_str)
            .text(formatDate(d.datetime));
    }

    // Add the X Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

});
