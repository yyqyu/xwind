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

        // Create a new div container for Notams
        newcontainer = document.createElement('div');
        newcontainer.setAttribute('class', 'col-12 mt-4');
        newcontainer.setAttribute('id', 'notam_container');
        document.getElementById('content').appendChild(newcontainer);
        // Ajax call getting notams
        $.ajax({
                type: "GET",
                url: '/notams_app',
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

        // Function used below to copy appropriate notam to clipboard
        function copyNotam (tooltipNumber, divName) {
            div = document.getElementById(divName);
                // Making sure there's no error otherwise function will stall
                if (div) {
                    // Add an on-click event listener on that div
                    div.addEventListener('click', function() {
                    var notamToCopy = document.getElementById(divName).innerHTML;
                    var regex = /<br\s*[\/]?>/gi;
                    // Replaced <br> that was added by a new line character for copy and pasting purposes
                    notamToCopy = notamToCopy.replace(regex, "\n");
                    // The code for the clipboard image will be present, so counting backwards from where
                    // it is found.
                    var imgcount = notamToCopy.search("<img");
                    notamToCopy = notamToCopy.substring(0, imgcount-1);
                    copyToClipBoard(notamToCopy);
                    document.getElementById(tooltipNumber).style.display = "inline";
                    // Remove tooltip after a second
                    setTimeout( function() {
                        document.getElementById(tooltipNumber).style.display = "none";
                        }, 1000);
                    });
                }
            }

        function checkIfEmpty(notam) {
            if (!notam) {
                return true;
            } else if (notam == " ") {
                return true;
            } else {
                return false;
            }
        }

        function isNavCanada(notam) {
            // Gotta iterate the 1 here.
            if (notam == 2) {
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

        function FAANotam(notam) {
            if ((notam != "") || (notam != " ")) {
                return notam;
            }
        }

        function writeFAANotam(notams_list) {
            for (var i = 0; i < notams_list.length; i++) {
                if ((notams_list != " ") || (notams_list != "")){
                    createDiv(notams_list[i], count);
                    count++;
                }
            }
        }

        function writeCanadianNotam(rsc, notams_list) {
            createDiv(rsc, count);
            count++;
            for (var i = 0; i < notams_list.length; i++, count++) {
                createDiv(notams_list[i], count);
            }
        }

        function createDiv(notam, count) {
            // Create div for displaying notam
            var newdiv = document.createElement('div');
            var divIdName = 'notam'+ count;
            newdiv.setAttribute('id', divIdName);
            newdiv.setAttribute('class', 'notam fira-font');
            newdiv.innerHTML = notam;
            // Append notam to the container
            document.getElementById('notam_container').appendChild(newdiv);
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
            tooltip.innerHTML = "Notam copied to clipboard";
            document.getElementById(divIdName).appendChild(tooltip);
            // Call function to copy the notam to the clipboard
            copyNotam(tooltipIdNumber, divIdName);
            count++;
        }

        // Put data received from ajax call onto HTML page
        function iterate(data){

            console.log(data);

            // How many notams to display total
            var notams_qty = data[0][0].length
            // console.log(notams_qty);

            // How many stations entered by user
            var stations_qty = data[0][2].length;
            // console.log(stations_qty);

            // List of stations entered by the user
            var stations_list = data[0][2];
            // console.log(stations_list);

            // How many (complete) stations name have been passed through
            var stations_list_names = data[0][1];
            // console.log(stations_list_names);

            // Total notam count
            var k = 0;
            for (var j = 0; j < stations_qty; j++) {
                // Write airport name on page
                writeAirportName(stations_list[j], stations_list_names[j]);
                var notams_list_canada = [];
                var notams_list_faa = [];
                for (var i = 0; i < notams_qty; i++) {
                    if (data[0][0][i][2] == "CANADA") {
                        if (data[0][0][i][1].includes(stations_list[j])) {
                            var canadian_notam = CanadianNotam(data[0][0][i][0]);
                            notams_list_canada.push(canadian_notam);
                            k++;
                        }
                    } else if (data[0][0][i][2] == "FAA"){
                        if (data[0][0][i][1].includes(stations_list[j])){
                            var faa_notam = FAANotam(data[0][0][i][0]);
                            notams_list_faa.push(faa_notam);
                            k++;
                       }
                    }
                }
                // RSC is always the last one, separating it from the rest.
                if (notams_list_canada != "") {
                    var rsc = notams_list_canada.pop();
                    writeCanadianNotam(rsc, notams_list_canada);
                }

                if (notams_list_faa != "") {
                    writeFAANotam(notams_list_faa.slice(1));
                }
            }












            // Add airport name and ICAO code
            // document.getElementById("airportname").innerHTML = (data[0][2] + " - " + data[0][3]);


            // Toggle state of table headers from hidden to seen
            // document.getElementById("time_dir_str").classList.add("seen");
            // document.getElementById("time_dir_str").classList.remove("hidden");
            // document.getElementById("table-header").classList.add("seen");
            // document.getElementById("table-header").classList.remove("hidden");
            // document.getElementById("previous").classList.add("seen");
            // document.getElementById("previous").classList.remove("hidden");
            // document.getElementById("next").classList.add("seen");
            // document.getElementById("next").classList.remove("hidden");

            // Toggle state of loading div once everything is finished loading
            document.getElementById("loading").classList.add("remove");
            document.getElementById("loading").classList.remove("seen");

            if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
                document.getElementById('airportname').scrollIntoView();
            }
        }

    })

    // Wait for page to finish loading
    window.addEventListener('load', function() {


        /* Watch #w-direction div for change
        (will trigger even if winds don't change since winds will still be removed and added by iterate function)*/
        var element = document.querySelector('#w-direction');


    // Define variables to work with in highlight function
    let search_term_pt1 = document.querySelector("#w-direction").textContent.padStart(3, '0');
    let search_term_pt2 = document.querySelector("#w-strength").textContent.padStart(2, '0');
    let search_term = (search_term_pt1 + search_term_pt2 + "KT");
    let results = document.querySelector("#wx");

    // Add mutation observer (multiple browser support)
    var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;

    // Call highlight function if any changes are made to w-direction div
    var observer = new MutationObserver(highlight);
    observer.observe(element, {
      childList: true
    });

    // Call highlight again if user manually changed one of the 2 wind divs
    var contentedited3 = document.querySelector("#w-direction");
    contentedited3.addEventListener('input', function() {
        highlight();
    });
    var contentedited4 = document.querySelector("#w-strength");
    contentedited4.addEventListener('input', function() {
        highlight();
    });

        function highlight() {
            // Update results, search_term_pt1 and search_term_pt2 when function is ran
            results.innerHTML = document.querySelector("#wx").innerHTML;
            search_term_pt1 = document.querySelector("#w-direction").textContent.padStart(3, '0');
            search_term_pt2 = document.querySelector("#w-strength").textContent.padStart(2, '0');

            // Replace a value of 0 by 00 for search purposes
            if (parseInt(search_term_pt2) == 0){
                search_term_pt2 = "00";
            }
            // Replace value of 000 by VRB in the search substring
            else if ((parseInt(search_term_pt2) <= 5) && (search_term_pt1 == "000")) {
                search_term_pt1 = "VRB";
            }

            search_term = (search_term_pt1 + search_term_pt2 + "KT");
            // Remove previous highlight tags in HTML
            results.innerHTML = results.innerHTML.replace(/<mark>/g,'');
            results.innerHTML = results.innerHTML.replace(/<\/mark>/g,'');
            // Highlight winds if found.
            results.innerHTML = results.innerHTML.replace(new RegExp(search_term, "gi"), (match) => `<mark>${match}</mark>`);
            // Check for gust and highlight winds containing them
            search_gust_string = (search_term_pt1 + search_term_pt2 + 'G\\d\\dKT');
            results.innerHTML = results.innerHTML.replace(new RegExp(search_gust_string, "gi"), (match) => `<mark>${match}</mark>`);
        }




    });
