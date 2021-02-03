// Script for the loader
var loader;
function pageLoader() {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    if (vars.length-1 > 1) {
        document.getElementById("loader").style.top = "75vh";
    }
    loader = setTimeout(showPage, 3000);
}
function showPage() {
    document.getElementById("loader").style.display = "none";
    document.getElementById("pageContent").style.display = "block";
}


// Get the HTML form used for filtering time slots
var form = document.getElementById("filterSlotsForm");


// Function that submits the form and displays filter available time slots
function submitForm() {
    document.getElementById("pageContent").style.display = "none";
    document.getElementById("loader").style.top = "75vh";
    document.getElementById("loader").style.display = "block";
    document.sform.action = window.location.href;
    return true;
}

// Function to set up of Jquery UI tooltip
function tooltipSetUp() {
    $(document).tooltip({
        tooltipClass: "moreInfo",
        show: {
            effect: "slideDown",
            delay: 250
        },
        position: {
            my: "center-36 bottom-20",
            at: "center top",
        }
    });
    // Stop log from displaying on page
    document.querySelectorAll('[role="log"]').forEach(function (log){
        log.style.display = "none";
    });
}

var name;
window.onload = function () {

    // Gets Neon event id from AOA url (the parent to the iframe) and reloads page
    if (getAllQueryVariables("Neon_event_id").length === 0) {
        var parentURL = document.referrer;
        var varIndex = parentURL.indexOf("event=");
        var Neon_event_id = parentURL.slice(varIndex + 6, parentURL.indexOf("&", varIndex));
        window.location.href = ("/?Neon_event_id=" + Neon_event_id);
    } else {
        pageLoader();
        tooltipSetUp();

        // Carries values in the cycling filter form over to the refreshed page when form is submitted
        var checkboxNames = getAllQueryVariableNames("on");
        for (name of checkboxNames) {
            document.getElementById(decodeURIComponent(name.replace(/\+/g, '%20'))).checked = true;
        }
        var numberInputsValues = getAllQueryVariables("number_input");
        for (var i = 0; i < numberInputsValues.length; i++) {
            document.getElementsByClassName("cyclingVar")[i].value = numberInputsValues[i];
        }

        // Displays message if there are no available time slots
        var timeSlotRows = document.getElementsByClassName("timeSlotRows");
        var row;
        for (row of timeSlotRows) {
            if (row.style.display !== "none") {
                document.getElementById("newUserMessage").style.display = "block";
                return;
            }
        }
        document.getElementById("noSlotsMessage").style.display = "inline-block";
        document.getElementById("newUserMessage").style.display = "none";
    }
};


// Function takes a value and returns an array of which url variables have the given value
function getAllQueryVariableNames(variableValue)
{
    var varNames = [];
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        if(pair[1] === variableValue){varNames.push(pair[0]);}
    }
    return varNames;
}


// Function takes a substring and returns an array of the url variables that have the given substring in it's name
function getAllQueryVariables(variableSubStr)
{
    var varValues = [];
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if(pair[0].includes(variableSubStr)){varValues.push(pair[1]);}
    }
    return varValues;
}