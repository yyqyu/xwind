    // Prevent "station" input field default action
    $('#stationform').submit(function (e) {
        e.preventDefault();
        return false;
    });


    // Only allow numbers in contenteditable table
    function testCharacter(event) {
      if ((event.keyCode >= 48 && event.keyCode <= 57 )) {
        return true;
      } else {
        return false;
      }
    }


    var data = [];
    var count = 0;
    // Async call for all data on form submit
    $('#stationform').on("submit", function() {
        // Add loading animation
        document.getElementById("loading").classList.add("seen");
        document.getElementById("loading").classList.remove("remove");
        // Hide divs where data from ajax call will be posted
        // Set variables back to zero
        data.length = 0;
        count = 0;
        form_data = document.getElementById('station').value;

        // Erase these 2 divs when function is ran again
        document.getElementById("weather_container").remove();
        document.querySelectorAll('.airportname').forEach(e => e.remove());

        // Function to write the appropriate airport name at the top of weather.
        function writeAirportName(ident, airport) {
            airportname = document.createElement('h4');
            airportname.setAttribute('class', airportname);
            airportname.setAttribute('id', 'airport-'+ ident);
            document.getElementById('weather_container').append(airportname);
            document.getElementById('airport-'+ ident).innerHTML = airport + " - (" + ident + ")";
        }

        // Create a new div container for weather
        newcontainer = document.createElement('div');
        newcontainer.setAttribute('class', 'col-12 mt-4');
        newcontainer.setAttribute('id', 'weather_container');
        document.getElementById('content').appendChild(newcontainer);
        // Ajax call getting weather
        $.ajax({
                type: "GET",
                url: '/weather_app',
                data: {form_data},
                dataType: 'json',
                cache: false,
                success: function(result) {
                    data.push(result);
                    iterate(data);
            }

        });

        // Custom copy-to-clipboard function
        const copyToClipBoard = (str) =>
        {
            const el = document.createElement('textarea');
            el.value = str;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
        };

        // Function used below to copy appropriate weather to clipboard
        function copyWeather (tooltipNumber, divName) {
            div = document.getElementById(divName);
                // Making sure there's no error otherwise function will stall
                if (div) {
                    // Add an on-click event listener on that div
                    div.addEventListener('click', function() {
                    var weatherToCopy = document.getElementById(divName).innerHTML;
                    var regex = /<br\s*[\/]?>/gi;
                    // Replaced <br> that was added by a new line character for copy and pasting purposes
                    weatherToCopy = weatherToCopy.replace(regex, "\n");
                    // The code for the clipboard image will be present, so counting backwards from where
                    // it is found.
                    var imgcount = weatherToCopy.search("<img");
                    weatherToCopy = weatherToCopy.substring(0, imgcount-1);
                    var last_p_count = weatherToCopy.search("</p");
                    weatherToCopy = weatherToCopy.substring(0, last_p_count);
                    var weather_length = weatherToCopy.length;
                    var first_p_count = weatherToCopy.search("weather_p");
                    weatherToCopy = weatherToCopy.substring(first_p_count+11, weather_length);

                    copyToClipBoard(weatherToCopy);
                    document.getElementById(tooltipNumber).style.display = "inline";
                    // Remove tooltip after a second
                    setTimeout( function() {
                        document.getElementById(tooltipNumber).style.display = "none";
                        }, 1000);
                    });
                }
            }

        function checkIfEmpty(weather) {
            if (!weather) {
                return true;
            } else if (weather == " ") {
                return true;
            } else {
                return false;
            }
        }


        function writeMetar(weather_list) {
            for (var i = 0; i < weather_list.length; i++, count++) {
                createDiv(weather_list[i], count);
            }
        }

        function writeTaf(weather_list) {
            for (var i = 0; i < weather_list.length; i++, count++) {
                createDiv(weather_list[i], count);
            }
        }


        function createDiv(weather, count) {
            // Create div for displaying weather
            var newdiv = document.createElement('div');
            var new_p = document.createElement('p');
            var p_class = "weather_p";
            var divIdName = 'weather'+ count;
            new_p.setAttribute('class', p_class);
            newdiv.setAttribute('id', divIdName);
            newdiv.setAttribute('class', 'weather fira-font');
            new_p.innerHTML = weather;
            // Append weather to the container
            document.getElementById('weather_container').appendChild(newdiv);
            document.getElementById(divIdName).appendChild(new_p);
            // Create clipboard image indicating possible copy to clipboard
            var clipboard = document.createElement("img");
            clipboard.src = '../static/media/clipboard.svg';
            clipboard.setAttribute('class', 'clipboard');
            document.getElementById(divIdName).appendChild(clipboard);
            // Create a tooltip to be appended to the right div
            tooltipIdNumber = "tooltip-" + count;
            var tooltip = document.createElement('span');
            tooltip.setAttribute('id', tooltipIdNumber);
            tooltip.setAttribute('class', 'custom-tooltip');
            // TODO: MODIFY METAR OR TAF DEPENDING ON WHAT IS BEING SELECTED
            tooltip.innerHTML = "Weather copied to clipboard";
            document.getElementById(divIdName).appendChild(tooltip);
            // Call function to copy the weather to the clipboard
            copyWeather(tooltipIdNumber, divIdName);
            count++;
        }

        function formatTaf(taf) {
            separate = taf.split(" ");
            formatted = [];
            for (var i = 0; i < separate.length; i++){
                if (separate[i].substring(0, 2) == "FM"){
                    formatted += ("\n" + separate[i] + " ");
                } else if (separate[i] == ("TEMPO" || "BECMG" || "PROB30" || "PROB40")){
                    formatted += ("\n" + separate[i] + " ");
                } else {
                    formatted += (separate[i] + " ");
                }
            }


            console.log(formatted);
            // new_text = ("".join(formatted))

            // new_text_row = new_text.split('\n')
            return formatted;
        }

        // Put data received from ajax call onto HTML page
        function iterate(data){

            // console.log(data);

            list_of_metars = data[0][0];
            metars_qty = data[0][0].length;
            console.log(list_of_metars);

            list_of_tafs = data[0][1];
            tafs_qty = data[0][1].length;
            console.log(list_of_tafs);

            stations_list_names = data[0][2];
            console.log(stations_list_names);

            stations_list = data[0][3];
            console.log(stations_list);
            weather_qty = 0;

            stations_qty = stations_list.length;

            // Total weather count
            var k = 0;
            for (var j = 0; j < stations_qty; j++) {
                // Write airport name on page
                writeAirportName(stations_list[j], stations_list_names[j]);
                var metar_list = [];
                var taf_list = [];
                for (var i = 0; i < metars_qty; i++) {
                        if (list_of_metars[i][1].includes(stations_list[j])) {
                            metar = list_of_metars[i][0];
                            metar_list.push(metar);
                            k++;
                        }
                }

                for (var i = 0; i < tafs_qty; i++) {
                        if (list_of_tafs[i][1].includes(stations_list[j])) {
                            taf = formatTaf(list_of_tafs[i][0]);
                            taf_list.push(taf);
                            k++;
                        }
                }

                if (metar_list != "") {
                    writeMetar(metar_list);
                }
                if (taf_list != "") {
                    writeTaf(taf_list);
                }
            }

            document.getElementById("loading").classList.add("remove");
            document.getElementById("loading").classList.remove("seen");

            if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
                document.getElementById('airportname').scrollIntoView();
            }

        }
    })
