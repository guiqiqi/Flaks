// global request and XML document objects
var peopleReq = "";
var eventsReq = "";
var myPeople = ["No one"];
var currName = "No one";

// handle receiving of event list
function processEventsReq() {
    // only if req shows "loaded"
    if (eventsReq.readyState == 4) {
        // only if "OK"
        if (eventsReq.status == 200) {

            var content = "<tr><th>Event Name</th><th>Event Description</th><th>Datetime</th></tr>";
            var myJSONTxt = eventsReq.responseText;
            var myEvents = JSON.parse(myJSONTxt);
            myEvents.sort(function(x, y){
                return x.datetime.localeCompare(y.datetime);
            })
            
            for (var i = 0; i < myEvents.length; i++) {
                content += "<tr>";
                content += "<td>" + unescape(decodeURI(myEvents[i].name)) + "</td>";
                content += "<td>" + unescape(decodeURI(myEvents[i].description)) + "</td>";
                content += "<td>" + myEvents[i].datetime + "</td>";
                content += "</tr>"
            }

            info = document.getElementById("events-no-data");
            info.style.display = "none";
            container = document.getElementById("events");
            // blast new HTML content into "details" <div>
            container.innerHTML = content;

        } else {
            alert("There was a problem retrieving the event data:\n" +
            eventsReq.statusText);
        }
    } 
}

function doEventRequest() {
    // TODO: insert event retrieval request
    eventsReq = new XMLHttpRequest();
    eventsReq.open("GET", "./events.cgi?name=" + currName);
    eventsReq.send()
    eventsReq.addEventListener("load", processEventsReq);
    
    // would be nice to remember each change...
    document.cookie = "person=" + currName;
}

// retrieve event list for the selected person
function loadEvents(event) {
    // get the key for the selected person
    currName = myPeople[event.target.value];
    doEventRequest();
}

// add item to select element the less
// elegant, but compatible way.
function appendToSelect(select, value, content, name)  {
    var opt;
    opt = document.createElement("option");
    opt.value = value;

    // make sure we select the current option -- not required but it looks better
    if ( name == currName ) opt.selected = true;
    opt.appendChild(content);
    select.appendChild(opt);
}


// fill People select list with items
function buildPeopleList() {
    var select = document.getElementById("people");
    var activeCurr = false;
    select.innerHTML = "";

    // add each person to the People select element
    for (var i = 0; i < myPeople.length; i++) {
        appendToSelect(select, i, document.createTextNode(myPeople[i]), myPeople[i] );
        if (myPeople[i] == currName)
            activeCurr = true;
    }
  
    // make sure that the current name we have from a cookie is still alive
    if (!activeCurr) currName = "No One";
}

// handle receiving of people list
function processPeopleReq() {

    // only if req shows "loaded"
    if (peopleReq.readyState == 4) {

        // only if "OK"
        if (peopleReq.status == 200) {
            var myJSONTxt = peopleReq.responseText;
            myPeople = JSON.parse(myJSONTxt);
            buildPeopleList();

            // only load events if we actually have data...
            if ( myPeople.length > 0 ) {

                // if we don't have a valid cookie, just pick the first one -- not required by assignment
                if (currName == "No One" && myPeople.length) {
                    currName = myPeople[0];
                }

                if (currName != "") {
                    doEventRequest();
                }
            }
            else {
                div = document.getElementById("events-no-data");
                div.innerHTML = "<br/> Choose person first.";
            }
        }
    }
}

function request_people() {
    peopleReq = new XMLHttpRequest();
    peopleReq.open("GET", "./people.cgi");
    peopleReq.send();
    peopleReq.addEventListener("load", processPeopleReq);
}

function addEvent() {
    var name = document.getElementById("person-name").value;
    var event_name = document.getElementById("event-name").value;
    var description = document.getElementById("description").value;
    var datetime = document.getElementById("event-time").value;

    params = new URLSearchParams();
    params.set("name", event_name);
    params.set("description", description);
    params.set("datetime", datetime);

    req = new XMLHttpRequest();
    req.open("POST", "./events.cgi?name=" + name);
    req.withCredentials = true;
    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    req.send(params.toString());
    req.addEventListener("load", request_people);
}

request_people();
