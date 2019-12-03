

    // When the user scrolls down 20px from the top of the document, show the button
    window.onscroll = function() {scrollFunction()};

    function scrollFunction() {
      if (document.body.scrollTop > 30 || document.documentElement.scrollTop > 30) {
        $('#backtotop').stop().fadeTo(300,1);

      } else {
        $('#backtotop').stop().fadeTo(300,0);
      }
    }


    // When the user clicks on the button, scroll to the top of the document
    function topFunction() {
      document.body.scrollTop = 0; // For Safari
      document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    }


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
        document.getElementById("time_dir_str").classList.add("hidden");
        document.getElementById("time_dir_str").classList.remove("seen");
        document.getElementById("table-header").classList.add("hidden");
        document.getElementById("table-header").classList.remove("seen");
        document.getElementById("previous").classList.add("hidden");
        document.getElementById("previous").classList.remove("seen");
        document.getElementById("next").classList.add("hidden");
        document.getElementById("next").classList.remove("seen");
        wxtypeandtime.classList.add("hidden");
        wxtypeandtime.classList.remove("seen");
        $("#rwy_table").empty();
        $("#taf").empty();
        $("#metar").empty();
        $("w-direction").empty();
        $("w-strength").empty();
        $("#airportname").empty();
        // Set variables back to zero
        data.length = 0;
        let counter1 = 0;
        let counter2 = 0;
        let counter3 = 0;
        let counter4 = 0;
        let counter5 = 0;
        $.ajax({
                type: "POST",
                url: '/?station=' + station.value,
                dataType: 'json',
                success: function(result) {
                    data.push(result);
                    iterate(data);
                    console.log(data);
            }

        });

        // Put data received from ajax call onto HTML page
        function iterate(data){

            // Add airport name and ICAO code
            document.getElementById("airportname").innerHTML = (data[0][2] + " - " + data[0][3]);

            // Add runways to leftmost column in table
            let rwy_list = data[0][4];
            let row_id = 0;
            $.each(rwy_list,function(key,value){
                $.each(value, function(key2, value2) {
                    $("#rwy_table").append(
                    "<tr id=row_id_" + row_id + ">" +
                    "<td class='fix-broken-table1 rwy_list'>" + value2 + "</td>");
                    row_id++;
                });
            });

            // Add rwy_data to runway tooltips
            let rwy_data = data[0][10];
            let n = 0;
            let ids = "row_id_" + n;
            $.each(rwy_data,function(index, value){
                    // Add data twice, for both directions of runway
                    ids = "row_id_" + n;
                    $("#" + ids).children(".rwy_list").attr("data-toggle", "tooltip");
                    $("#" + ids).children(".rwy_list").attr("data-placement", "bottom");
                    $("#" + ids).children(".rwy_list").attr("title", value);
                    n++;
                    ids = "row_id_" + n;
                    $("#" + ids).children(".rwy_list").attr("data-toggle", "tooltip");
                    $("#" + ids).children(".rwy_list").attr("data-placement", "bottom");
                    $("#" + ids).children(".rwy_list").attr("title", value);
                    n++;
                });
            // Activate all tooltips from Bootstraps
            $('[data-toggle="tooltip"]').tooltip();

            // Add metar text to page
            document.getElementById("metar").innerHTML = data[0][0];

            // Add taf text to page line by line (TAF was rearranged in backend)
            let taf = data[0][1];
            taf.forEach(function(item){
                $("#taf").append("<li>" + item + "</li>");
            });


            // Add wind direction to first conenteditable cell
            let wind_dir = document.getElementById("w-direction");

            // If no weather, inputs nothing instead of double 00
            function direction(data) {
                if (data[0][6][counter1].length == 1) {
                    $('#w-direction').html("0");
                }
                else {
                    $('#w-direction').html(data[0][6][counter1].padStart(3, '0'));
                }
            }

            direction(data);
            $('#next').click(function() {
                if (counter1 < (data[0][6].length - 1)) {
                counter1++;
                $('#w-direction').empty();
                direction(data);
                }
            });
            $('#previous').click(function() {
                if(counter1>0){
                counter1--;
                $('#w-direction').empty();
                direction(data);
                }
            });

            // Add wind strength to second conenteditable cell
            let wind_str = document.getElementById("w-strength");
            /* wind_str.innerHTML = (data[0] + ' kt'); <-- If I want to add kt at the end.
                                                         (But what if user manually change winds?)*/

            // If no weather, inputs nothing instead of double 00
            function strength(data) {
                if (data[0][7][counter2] == " ") {
                    $('#w-strength').html("");
                }
                else {
                    $('#w-strength').html(data[0][7][counter2]);
                }
            }

            strength(data);
            $('#next').click(function() {
                if (counter2 < (data[0][7].length - 1)) {
                counter2++;
                $('#w-strength').empty();
                $('#w-strength').html(data[0][7][counter2]);
                }
            });
            $('#previous').click(function() {
                if(counter2>0){
                counter2--;
                $('#w-strength').empty();
                $('#w-strength').html(data[0][7][counter2]);
                }
            });


            // Add wx_time to wx_dir_str div
            var wx_time = document.getElementById("wx_time");
            wx_time.innerHTML = data[0][8][counter3];
            $('#next').click(function() {
                if (counter3 < (data[0][8].length - 1)) {
                counter3++;
                $('#wx_time').empty();
                $('#wx_time').html(data[0][8][counter3]);
                }
            });
            $('#previous').click(function() {
                if(counter3>0){
                counter3--;
                $('#wx_time').empty();
                $('#wx_time').html(data[0][8][counter3]);
                }
            });

            // Add wx_type to wx_dir_str div
            let wx_type = document.getElementById("wx_type");
            wxtypeandtime.classList.add("seen");
            wxtypeandtime.classList.remove("hidden");
            wx_type.innerHTML = data[0][9][counter4];
            $('#next').click(function() {
                if (counter4 < (data[0][9].length - 1)) {
                counter4++;
                $('#wx_type').empty();
                $('#wx_type').html(data[0][9][counter4]);
                }
            });
            $('#previous').click(function() {
                if(counter4>0){
                counter4--;
                $('#wx_type').empty();
                $('#wx_type').html(data[0][9][counter4]);
                }
            });

            // Get a list of headings in SAME ORDER as runway_list
            let headings_list = [];
            $.each(data[0][5], function(key, value){
                $.each(value, function(key2, value2) {
                    headings_list.push(value2);
                });
            });

            // Function to calculate headwind, crosswinds, and minimums CRFI
            function calculate(data) {
                let rwy_headings = data[0][5];
                var num = 0;
                let id = "row_id_" + num;
                let wind_speed = 0;
                let wind = 0;
                let crosswind = 0;
                let headwind = 0;
                let min_crfi = 0;
                let to_rad = (Math.PI / 180);
                $.each(rwy_headings,function(key_h,value_h){
                    $.each(value_h, function(key_h_2, value_h_2) {
                        wind = parseInt(document.querySelector("#w-direction").innerHTML);
                        wind_speed = parseInt(document.querySelector("#w-strength").innerHTML);
                        if (wind == 0){
                            crosswind = 0;
                            headwind = 0;
                        }
                        else {
                            crosswind = Math.abs(wind_speed * Math.sin((value_h_2 - wind)* to_rad));
                            headwind = (wind_speed * Math.cos((value_h_2 - wind)* to_rad));
                        }

                        // Check if crosswind is over 45 knots
                        if (crosswind > 45) {
                            min_crfi = "Off charts";
                        }
                        else {
                            min_crfi = interpolate(crosswind);
                            min_crfi = Math.round(min_crfi*100)/100;
                        }

                        // Write "-" if NaN, instead of simply NaN, for aesthetic purposes
                        if ((Number.isNaN(crosswind) == true) || (Number.isNaN(headwind) == true)) {
                            $("#" + id).children(".fix-broken-table3").remove();
                            $("#" + id).append(
                            "<td class='fix-broken-table3 head'>"+ "-" +"</td>" +
                            "<td class='fix-broken-table3 cross'>"+ "-" + "</td>" +
                            "<td class='fix-broken-table3 CRFI'>"+ "-" + "</td>");
                            num++;
                            id = "row_id_" + num;
                        }
                        else {
                            $("#" + id).children(".fix-broken-table3").remove();
                            $("#" + id).append(
                            "<td class='fix-broken-table3 head'>"+ Math.round(headwind*10)/10 +"</td>" +
                            "<td class='fix-broken-table3 cross'>"+ Math.round(crosswind*10)/10 + "</td>" +
                            "<td class='fix-broken-table3 CRFI'>"+ min_crfi+ "</td>");
                            num++;
                            id = "row_id_" + num;
                        }

                    });
                });
            }

            // Makes calculations when Next or Previous is clicked
            calculate(data);
            background();
            $('#next').click(function() {
                calculate(data);
                background();
            });
            $('#previous').click(function() {
                calculate(data);
                background();
            });
            // Makes calculations when user inputs a new value
            let contentedited1 = document.querySelector("#w-direction");
            contentedited1.addEventListener('input', function() {
                calculate(data);
                background();
                wx_type.innerHTML = "MANUAL INPUT";
                $('#wx_time').empty();

            });
            let contentedited2 = document.querySelector("#w-strength");
            contentedited2.addEventListener('input', function() {
                calculate(data);
                background();
                wx_type.innerHTML = "MANUAL INPUT";
                $('#wx_time').empty();
            });

            // Toggle state of table headers from hidden to seen
            document.getElementById("time_dir_str").classList.add("seen");
            document.getElementById("time_dir_str").classList.remove("hidden");
            document.getElementById("table-header").classList.add("seen");
            document.getElementById("table-header").classList.remove("hidden");
            document.getElementById("previous").classList.add("seen");
            document.getElementById("previous").classList.remove("hidden");
            document.getElementById("next").classList.add("seen");
            document.getElementById("next").classList.remove("hidden");

            // Toggle state of loading div once everything is finished loading
            document.getElementById("loading").classList.add("remove");
            document.getElementById("loading").classList.remove("seen");


            document.getElementById('airportname').scrollIntoView();

            // Interpolate between different values for Min CRFI calculation
            function interpolate(crosswind) {
                if (crosswind <= 10){
                    let lower_crfi = 0.2;
                    let higher_crfi = 0.3;
                    let crfi_gap = higher_crfi - lower_crfi;
                    let lower_wind = 0;
                    let higher_wind = 10;
                    let wind_gap = higher_wind - lower_wind;
                    let min_crfi =  lower_crfi + ((crosswind - lower_wind) / wind_gap) * crfi_gap ;
                    return min_crfi;
                }
                else if ((crosswind > 10) && (crosswind <= 15)) {
                    let lower_crfi = 0.3;
                    let higher_crfi = 0.4;
                    let crfi_gap = higher_crfi - lower_crfi;
                    let lower_wind = 10;
                    let higher_wind = 15;
                    let wind_gap = higher_wind - lower_wind;
                    let min_crfi = lower_crfi + ((crosswind - lower_wind) / wind_gap) * crfi_gap;
                    return min_crfi;
                }
                else if ((crosswind > 15) && (crosswind <= 35)) {
                    let lower_crfi = 0.4;
                    let higher_crfi = 0.6;
                    let crfi_gap = higher_crfi - lower_crfi;
                    let lower_wind = 15;
                    let higher_wind = 35;
                    let wind_gap = higher_wind - lower_wind;
                    let min_crfi = lower_crfi + ((crosswind - lower_wind) / wind_gap) * crfi_gap;
                    return min_crfi;
                }
                else if ((crosswind > 35) && (crosswind <= 40)) {
                    let lower_crfi = 0.6;
                    let higher_crfi = 0.7;
                    let crfi_gap = higher_crfi - lower_crfi;
                    let lower_wind = 35;
                    let higher_wind = 40;
                    let wind_gap = higher_wind - lower_wind;
                    let min_crfi = lower_crfi + ((crosswind - lower_wind) / wind_gap) * crfi_gap;
                    return min_crfi;
                }
                else if ((crosswind > 40) && (crosswind <= 45)) {
                    let lower_crfi = 0.7;
                    let higher_crfi = 0.75;
                    let crfi_gap = higher_crfi - lower_crfi;
                    let lower_wind = 40;
                    let higher_wind = 45;
                    let wind_gap = higher_wind - lower_wind;
                    let min_crfi = lower_crfi + ((crosswind - lower_wind) / wind_gap) * crfi_gap;
                    return min_crfi;
                }
            }

            // Function to add backgound coloring when headwind or crosswind changes
            function background() {
                headtailwind_divs = document.getElementsByClassName("head");
                crosswind_divs = document.getElementsByClassName("cross");
                CRFI_divs = document.getElementsByClassName("CRFI");
                for (var i=0; i < headtailwind_divs.length; i++) {
                    if ((headtailwind_divs[i].innerHTML < 0) && (headtailwind_divs[i].innerHTML > -10)) {
                        if (headtailwind_divs[i].classList.contains("tailwind") == false) {
                            headtailwind_divs[i].classList.add("tailwind");
                        }
                    }
                    else if (headtailwind_divs[i].innerHTML <= -10) {
                        if (headtailwind_divs[i].classList.contains("tailwind_strong") == false) {
                            headtailwind_divs[i].classList.add("tailwind_strong");
                        }
                    }
                    /*else if (headtailwind_divs[i].innerHTML >= 0) {
                        if (headtailwind_divs[i].classList.contains("headwind") == false) {
                            headtailwind_divs[i].classList.add("headwind");
                        }
                    }*/
                }

                for (var j = 0; j < crosswind_divs.length; j++){
                    if (crosswind_divs[j].innerHTML >= 20) {
                        if (crosswind_divs[j].classList.contains("crosswind_strong") == false) {
                            crosswind_divs[j].classList.add("crosswind_strong")
                        }
                    }
                    else if ((crosswind_divs[j].innerHTML >= 10) && (crosswind_divs[j].innerHTML < 20)) {
                        if (crosswind_divs[j].classList.contains("crosswind_medium") == false) {
                            crosswind_divs[j].classList.add("crosswind_medium")
                        }
                    }
                }
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


