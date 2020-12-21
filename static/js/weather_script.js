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

    // Prevent inputting more than 3 characters in table
    //$('#w-direction').on("keypress", function (e) {
    //    if (this.innerHTML.length > 3) {
    //        e.preventDefault();
    //        return false;
    //    }
    // });

    // Prevent inputting more than 3 characters
    //$('#w-strength').on("keypress", function (e) {
    //    if (this.innerHTML.length > 3) {
    //        e.preventDefault();
    //        return false;
    //    }
    // });

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
        document.getElementById("notam_container").remove();
        document.querySelectorAll('.airportname').forEach(e => e.remove());

        // Function to write the appropriate airport name at the top of notams.
        function writeAirportName(ident, airport) {
            airportname = document.createElement('h4');
            airportname.setAttribute('class', airportname);
            airportname.setAttribute('id', 'airport-'+ ident);
            document.getElementById('notam_container').append(airportname);
            document.getElementById('airport-'+ ident).innerHTML = airport + " - (" + ident + ")";
        }

        // Create a new div container for weather
        newcontainer = document.createElement('div');
        newcontainer.setAttribute('class', 'col-12 mt-4');
        newcontainer.setAttribute('id', 'weather_container');
        document.getElementById('content').appendChild(newcontainer);
        // Ajax call getting notams
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
                    imgcount = weatherToCopy.search("<img");
                    notamToCopy = weatherToCopy.substring(0, imgcount-1);
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

        function CanadianNotam(notam) {
            notam = notam.replace(/\\n/g, "<br />")
            if (notam.includes("NOTAMJ") == false) {
                notam = notam.substring(11, notam.length-1);
            }

            // Remove French notams part.
            if (notam.includes("FR:") == true) {
                var distance = notam.search("FR:");
                notam = notam.substring(0, distance-2);
            }

            // If error on NavCanada's part and there are still "english: null" or
            // "french: null" in notam, remove it.
            if (notam.includes("null") == true) {
                var distance = notam.search("null");
                notam = notam.substring(0, distance-16);
            }
            // notam = notam + ")";
            return notam;
        }


        function writeWeather(weather_list) {
            for (var i = 0; i < weather_list.length; i++, count++) {
                createDiv(weather_list[i], count);
            }
        }

        function createDiv(weather, count) {
            // Create div for displaying weather
            var newdiv = document.createElement('div');
            var divIdName = 'weather'+ count;
            newdiv.setAttribute('id', divIdName);
            newdiv.setAttribute('class', 'weather fira-font');
            newdiv.innerHTML = weather;
            // Append weather to the container
            document.getElementById('weather_container').appendChild(newdiv);
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

        // Put data received from ajax call onto HTML page
        function iterate(data){

            console.log(data);

            weather_qty = 0;

            // Total weather count
            var k = 0;
            for (var j = 0; j < stations_qty; j++) {
                // Write airport name on page
                writeAirportName(stations_list[j], stations_list_names[j]);
                var weather_list = [];
                for (var i = 0; i < weather_qty; i++) {
                        if (data[0][0][i][1].includes(stations_list[j])) {
                            // var formattedweather = // Format weather with(data[0][0][i][0]);
                            // weather_list.push(formattedweather);
                            k++;
                        }
                }

                if (weather_list != "") {
                    // writeWeather(weather_list);
                }
            }
        }
    })