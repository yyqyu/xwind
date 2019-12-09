var username = document.getElementsByName('username')[0];
var registration = document.getElementById('registration');
var pw1 = document.getElementsByName('password')[0];
var pw2 = document.getElementsByName('confirmation')[0];

$('#usrchk').keyup(function() {
    $.get('/check?username=' + username.value, function(data) {
        if (data == false) {
            username.className = "form-control is-invalid";
            document.getElementById("usrinval").innerHTML = "Username is not available";
        } else if (data == true) {
            username.className = "form-control is-valid";
        }
    });
});

function validateform(e) {
    e.preventDefault();
    if (username.value == "") {
        document.getElementById("usrinval").innerHTML = "Please enter a username";
        username.className = "form-control is-invalid";
    }


    if (username.className == "form-control is-valid") {
        if (pw1.value.length > 0) {
            if (pw1.value == pw2.value) {
                pw1.className = "form-control is-valid";
                pw2.className = "form-control is-valid";
                document.getElementById('registration').submit();
            } else {
                pw2.className = "form-control is-invalid";
            }
            pw1.className = "form-control is-valid";
        } else if (pw1.value != pw2.value) {
            pw2.className = "form-control is-invalid";

        } else {
            pw1.className = "form-control is-invalid";
            pw2.className = "form-control";
        }
    }
}
registration.addEventListener('submit', validateform);