
var j = 0;

window.onload = window.onresize = function () {
    document.getElementById("container").innerHTML="";
    var newsvg = document.createElement('div');
    var newtag = document.createElement('div');
    newsvg.setAttribute('class', "svg");
    newtag.setAttribute('id', 'tag');
    document.getElementById("container").appendChild(newsvg);
    document.getElementById("container").appendChild(newtag);
    var w = window.innerWidth - 10;

    var svg = d3.selectAll(".svg")
    //.selectAll("svg")
    .append("svg")
    .attr("width", w)
    .attr("height", h)
    .attr("class", "svg");


      var taskArray = [
    {
      task: "CYMX - CYVO",
      type: "C-GNLA",
      startTime: new Date("Sun Dec 09 08:00:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 09:00:00 GMT 2020"),
      details: "Insert useful stuff here"
    },

    {
      task: "CYVO - CYYQ",
      type: "C-GNLA",
      startTime: new Date("Sun Dec 09 09:30:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 12:00:00 GMT 2020"),
      details: "Insert useful stuff here"
    },

    {
      task: "CYYQ - CMB2",
      type: "C-GNLA",
      startTime: new Date("Sun Dec 09 12:25:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 14:30:00 GMT 2020"),
      details: "Insert useful stuff here"
    },

    {
      task: "CMB2 - CYVO",
      type: "C-GNLA",
      startTime: new Date("Sun Dec 09 15:00:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 18:00:00 GMT 2020"),
    },

    {
      task: "CYZF - CDK2",
      type: "C-GNRD",
      startTime: new Date("Sun Dec 09 08:00:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 11:00:00 GMT 2020"),
      details: "Insert useful stuff here"
    },

    {
      task: "CDK2 - CYZF",
      type: "C-GNRD",
      startTime: new Date("Sun Dec 09 14:00:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 14:30:00 GMT 2020"),
    },

    {
      task: "CYEG - CYYC",
      type: "C-GTUK",
      startTime: new Date("Sun Dec 09 15:00:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 21:00:00 GMT 2020"),
      details: "Insert useful stuff here"
    },

    {
      task: "CYYC - CYVR",
      type: "C-GTUK",
      startTime: new Date("Sun Dec 09 21:25:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 22:25:00 GMT 2020"),
    },
    {
      task: "CYMX - CYYZ",
      type: "C-GNLE",
      startTime: new Date("Sun Dec 09 06:30:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 09:00:00 GMT 2020"),
      details: "Insert useful stuff here"
    },

    {
      task: "CYYZ - CYQB",
      type: "C-GNLE",
      startTime: new Date("Sun Dec 09 10:20:00 GMT 2020"), //year/month/day
      endTime: new Date("Sun Dec 09 10:55:00 GMT 2020"),
    },

    ];


    var dateFormat = d3.time.format("%Y-%m-%d");

    var timeScale = d3.time.scale()
          .domain([d3.min(taskArray, function(d) {return (d.startTime);}),
                   d3.max(taskArray, function(d) {return (d.endTime);})])
          .range([0,w-150]);

    var categories = new Array();

    for (var i = 0; i < taskArray.length; i++){
      categories.push(taskArray[i].type);
    }

    var catsUnfiltered = categories; //for vert labels

    categories = checkUnique(categories);

    var h = (checkUnique(categories).length) * 100;

    makeGant(taskArray, w, h);

    var title = svg.append("text")
                .text("Timeline Prototype")
                .attr("x", w/2)
                .attr("y", 25)
                .attr("text-anchor", "middle")
                .attr("font-size", 18)
                .attr("fill", "#009FFC");



    function makeGant(tasks, pageWidth, pageHeight){

    var barHeight = 20;
    var gap = barHeight + 4;
    var topPadding = 75;
    var sidePadding = 75; // space between y-axis label and rectangles

    var colorScale = d3.scale.linear()
      .domain([0, categories.length])
      .range(["#00B9FA", "#F95002"])
      .interpolate(d3.interpolateHcl);

    makeGrid(sidePadding, topPadding, pageWidth, pageHeight);
    drawRects(tasks, gap, topPadding, sidePadding, barHeight, colorScale, pageWidth, pageHeight);
    vertLabels(gap, topPadding, sidePadding, barHeight, colorScale);

    }


    function drawRects(theArray, theGap, theTopPad, theSidePad, theBarHeight, theColorScale, w, h){

    var bigRects = svg.append("g")
      .selectAll("rect")
     .data(theArray)
     .enter()
     .append("rect")
     .attr("x", 0)
     .attr("y", function(d, i){
         var cat_now = taskArray[i].type;
         var cat_previous;
         if (i != 0) {
           cat_previous = taskArray[i-1].type;
         }

         if (cat_now == cat_previous) {
           return j*theGap + 14 + theTopPad;
         } else {
           j = i;
           return j*theGap + 14 + theTopPad;
         }
    })
     .attr("width", function(d){
        return w-theSidePad/2;
     })
     .attr("height", theGap) // It implements a bunch of rectangle depending on how often category appears.
     .attr("stroke", "none")
     /*
     .attr("fill", function(d){
      for (var i = 0; i < categories.length; i++){
          if (d.type == categories[i]){
            return d3.rgb(theColorScale(i));
          }
      }
     })
     */
     .attr("opacity", 0);


       var rectangles = svg.append('g')
       .selectAll("rect")
       .data(theArray)
       .enter();


     var innerRects = rectangles.append("rect")
               .attr("rx", 3)
               .attr("ry", 3)
               .attr("x", function(d){
                return timeScale((d.startTime)) + theSidePad;
                })
                // Y Attribute, made it so it jumps when changing categories
               .attr("y", function(d, i){
                 var stack = taskArray[i].type;
                 var stack2;
                 if (i != 0) {
                   stack2 = taskArray[i-1].type;
                 } else {
                   stack2 = taskArray[i].type;
                 }
                 if (stack == stack2) {
                   return j*(theGap) - (theTopPad * 1.5) - 7;
                 } else {
                   j++;
                   return j*(theGap) - (theTopPad * 1.5) - 7;
                 }
              })
               .attr("width", function(d){
                  return (timeScale((d.endTime))-timeScale((d.startTime)));
               })
               .attr("height", theBarHeight)
               .attr("stroke", "none")
               .attr("fill", function(d){
                for (var i = 0; i < categories.length; i++){
                    if (d.type == categories[i]){
                      return d3.rgb(theColorScale(i));
                    }
                }
               })


           var rectText = rectangles.append("text")
                 .text(function(d){
                  return d.task;
                 })
                 .attr("x", function(d){
                  return (timeScale((d.endTime))-timeScale((d.startTime)))/2 + timeScale((d.startTime)) + theSidePad;
                  })
               // Y Attribute, made it so it jumps when changing categories
               .attr("y", function(d, i){
                   var stack = taskArray[i].type;
                   var stack2;
                   if (i != 0) {
                     stack2 = taskArray[i-1].type;
                   } else {
                     stack2 = taskArray[i].type;
                   }
                   if (stack == stack2) {
                     return j*(theGap) - (theTopPad * 1.5)-66;
                   } else {
                     j++;
                     return j*(theGap) - (theTopPad * 1.5)-66;
                   }

              })
                 .attr("font-size", 11)
                 .attr("text-anchor", "middle")
                 .attr("text-height", theBarHeight)
                 .attr("fill", "#fff");


    rectText.on('mouseover', function(e) {
    // console.log(this.x.animVal.getItem(this));
                 var tag = "";

           if (d3.select(this).data()[0].details != undefined){
            tag = "Flight: " + d3.select(this).data()[0].task + "<br/>" +
                  "Plane: " + d3.select(this).data()[0].type + "<br/>" +
                  "ETD: " + d3.select(this).data()[0].startTime + "<br/>" +
                  "ETA: " + d3.select(this).data()[0].endTime + "<br/>" +
                  "Details: " + d3.select(this).data()[0].details;
           } else {
            tag = "Flight: " + d3.select(this).data()[0].task + "<br/>" +
                  "Plane: " + d3.select(this).data()[0].type + "<br/>" +
                  "ETD: " + d3.select(this).data()[0].startTime + "<br/>" +
                  "ETA: " + d3.select(this).data()[0].endTime;
           }
           var output = document.getElementById("tag");

            var x = this.x.animVal.getItem(this) + "px";
            var y = this.y.animVal.getItem(this) + 25 + "px";

           output.innerHTML = tag;
           output.style.top = y;
           output.style.left = x;
           output.style.display = "block";
         }).on('mouseout', function() {
           var output = document.getElementById("tag");
           output.style.display = "none";
               });


    innerRects.on('mouseover', function(e) {
    //console.log(this);
           var tag = "";

           if (d3.select(this).data()[0].details != undefined){
               tag = "Flight: " + d3.select(this).data()[0].task + "<br/>" +
                     "Plane: " + d3.select(this).data()[0].type + "<br/>" +
                     "ETD: " + d3.select(this).data()[0].startTime + "<br/>" +
                     "ETA: " + d3.select(this).data()[0].endTime + "<br/>" +
                     "Details: " + d3.select(this).data()[0].details;
           } else {
               tag = "Flight: " + d3.select(this).data()[0].task + "<br/>" +
                     "Plane: " + d3.select(this).data()[0].type + "<br/>" +
                     "ETD: " + d3.select(this).data()[0].startTime + "<br/>" +
                     "ETA: " + d3.select(this).data()[0].endTime;
           }
           var output = document.getElementById("tag");

           var x = (this.x.animVal.value + this.width.animVal.value/2) + "px";
           var y = this.y.animVal.value + 25 + "px";

           output.innerHTML = tag;
           output.style.top = y;
           output.style.left = x;
           output.style.display = "block";
         }).on('mouseout', function() {
           var output = document.getElementById("tag");
           output.style.display = "none";

    });



    } // END OF drawRects functions


    function makeGrid(theSidePad, theTopPad, w, h){

    var xAxis = d3.svg.axis()
      .scale(timeScale)
      .orient('bottom')
      .ticks(d3.time.hours, 1)
      .tickSize(-h+theTopPad+20, 0, 0)
      .tickFormat(d3.time.format('%H00'));

    var grid = svg.append('g')
      .attr('class', 'grid')
      .attr('transform', 'translate(' +theSidePad + ', ' + (h - 50) + ')')
      .call(xAxis)
      .selectAll("text")
              .style("text-anchor", "middle")
              .attr("fill", "#000")
              .attr("stroke", "none")
              .attr("font-size", 10)
              .attr("dy", "1em");
    }

    function vertLabels(theGap, theTopPad, theSidePad, theBarHeight, theColorScale){
    var numOccurances = new Array();
    var prevGap = 0;

    for (var i = 0; i < categories.length; i++){
      numOccurances[i] = [categories[i], getCount(categories[i], categories)];
    }

    var axisText = svg.append("g") //without doing this, impossible to put grid lines behind text
     .selectAll("text")
     .data(numOccurances)
     .enter()
     .append("text")
     .text(function(d){
      return d[0];
     })
     .attr("x", 0)
     .attr("y", function(d, i){
      if (i > 0){
          for (var j = 0; j < i; j++){
            prevGap += numOccurances[i-1][1];
           // console.log(prevGap);
            return d[1]*theGap/2 + prevGap*theGap + theTopPad;
          }
      } else{
      return d[1]*theGap/2 + theTopPad;
      }
     })
     .attr("font-size", 11)
     .attr("text-anchor", "start")
     .attr("text-height", 14)
     .attr("fill", function(d){
      for (var i = 0; i < categories.length; i++){
          if (d[0] == categories[i]){
          //  console.log("true!");
            return d3.rgb(theColorScale(i)).darker(); // Instead of cycling thru for different colors no reason, would add another field and color it based on that
          }
      }
     });

    }

    //from this stackexchange question: http://stackoverflow.com/questions/1890203/unique-for-arrays-in-javascript
    function checkUnique(arr) {
      var hash = {}, result = [];
      for ( var i = 0, l = arr.length; i < l; ++i ) {
          if ( !hash.hasOwnProperty(arr[i]) ) { //it works with objects! in FF, at least
              hash[ arr[i] ] = true;
              result.push(arr[i]);
          }
      }
      return result;
    }

    //from this stackexchange question: http://stackoverflow.com/questions/14227981/count-how-many-strings-in-an-array-have-duplicates-in-the-same-array
    function getCounts(arr) {
      var i = arr.length, // var to loop over
          obj = {}; // obj to store results
      while (i) obj[arr[--i]] = (obj[arr[i]] || 0) + 1; // count occurrences
      return obj;
    }

    // get specific from everything
    function getCount(word, arr) {
      return getCounts(arr)[word] || 0;
    }


}
