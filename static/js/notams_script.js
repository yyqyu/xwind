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
    // Async call for all data on form submit
    $('#stationform').on("submit", function() {
        // Add loading animation
        document.getElementById("loading").classList.add("seen");
        document.getElementById("loading").classList.remove("remove");
        // Hide divs where ajax data will be posted
        // Set variables back to zero
        data.length = 0;
        form_data = document.getElementById('station').value;

        // Erase these 2 divs when function is ran again
        document.getElementById("notam_container").remove();
        document.getElementById("airport_name").remove();

        // Create a new div for airport name
        airportname = document.createElement('div');
        airportname.setAttribute('class', 'col-12 mt-4');
        airportname.setAttribute('id', 'airport_name');
        document.getElementById('content').appendChild(airportname);

        // Create a new div container for Notams
        newcontainer = document.createElement('div');
        newcontainer.setAttribute('class', 'col-12 mt-4');
        newcontainer.setAttribute('id', 'notam_container');
        document.getElementById('content').appendChild(newcontainer);
        $.ajax({
                type: "GET",
                url: '/notams_app',
                data: {form_data},
                dataType: 'json',
                cache: false,
                success: function(result) {
                    data.push(result);
                    iterate(data);
                    console.log(data);
            }

        });



        // Put data received from ajax call onto HTML page
        function iterate(data){
            console.log(data[0][0].length);
            console.log(data[0][1]);
            notams_qty = data[0][0].length;

            name = data[0][1];
            airportname.innerHTML = name;

            for (var i = 0; i < notams_qty - 1 + 1; i++) {
                newdiv = document.createElement('div');
                divIdName = 'notam'+i;
                newdiv.setAttribute('id', divIdName);
                newdiv.setAttribute('class', 'notam');
                newdiv.innerHTML = data[0][0][i][0] + ")";
                document.getElementById('notam_container').appendChild(newdiv);            
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


