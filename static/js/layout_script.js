$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

footer = document.getElementById("footer");
footer.innerHTML = "<br><br><br><br><br><br><br><br><br><br><br> &copy " + (new Date().getFullYear()) + " Xwind" + "<br><br><br>";