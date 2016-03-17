/**
 * Created by mattezovski on 7/15/15.
 */

var hasLocationServicesAvailable = true;
var destPanelEnabled = false;

function updateOnServer(url, id, data, cb) {
    var method = id ? 'PUT' : 'POST'
    $.ajax({
        url: id ? url + '/' + id.toString() : url,
        type: method,
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (respData) {
            cb(respData)
        }
    });
}

function getEtaFromRemainingTime(remainingTime) {

    var currentDate = new Date();
    var arrivalTime = currentDate.getTime() + remainingTime*60*1000;
    arrivalTime = new Date(arrivalTime);

    return arrivalTime;

}

function updateLocation(cb) {
    if (navigator.geolocation && hasLocationServicesAvailable) {
        //Get location from actual location service

        navigator.geolocation.getCurrentPosition(function (location) {
            current_lat = location.coords.latitude;
            current_long = location.coords.longitude;
            if (cb) {
                cb();
            }
        }, function () {
            alert("ETAFun is less fun without location services enabled. Please turn them on.");
            hasLocationServicesAvailable = false;
        });

        // Gotten through initialization. If this is desktop, simulate position changes for now.
        if (!WURFL.is_mobile) {
            hasLocationServicesAvailable = false;
        }

    }
    else {
        //Take current global location and increment for demo purposes

        current_lat += 0.01;
        current_long += 0.01;
        if (cb){
            cb();
        }
    }
}

function markSelfAsArrived() {

    if (ugsId) {
        ugsStatus = 'ARRIVED'
        refreshEta();
    }

}

function setSelfArrivalTimeFromUgsList(ugsList) {
    ugs = _.first(_.where(ugsList, {
        id: ugsId
    }));
    if (!ugs) {
        return;
    }
    if (ugsStatus == 'IS_GOING') {
        // Since the user has associated, enable the join-panel.
        enableDestStuff();
    }
    // We are associated with the session, so hide the helpers for getting associated.
    $('#select-or-add-text').hide();
    $('#add-self-button').hide();
    var arrivalTime = convertTimestampToLocalTime(ugs.last_eta);
    $('#arrival-time-me').text(arrivalTime);
    //Set manual selection. Field will be hidden if not relevant.
    if (ugs.last_manual_eta) {
        //Maybe this should be kept in Angular land?
        $('#my-eta-select').val(ugs.last_manual_eta.substring(0, 5));
    }

    // Set up views properly.
    if (ugs.eta_mode == 'MANUAL') {
        $('#manual-entry-button').click();
        $('#manual-entry-button').addClass('active');
    }
    else {
        if (ugs.transit_mode == 'CAR') {
            $('#depart-car-button').addClass('active');
        }
        else {
            $('#depart-walking-button').addClass('active');
        }
    }
}

function convertTimestampToLocalTime(ts) {
    // Takes a UTC timestamp and converts it to whatever the client's current time zone is.

    return moment.utc(ts, 'HH:mm:ss').local().format('h:mm A');
}

function switchToDiffUser(id) {

    $.get('/login/' + id + '/', function () {
        // After we have switched users, reload the page. Allows for state reset, etc.
        // TODO: Don't do full page reload. Make this more deliberate.

        location.reload();
    });

}

function addUserList(users) {
    var data = {
        'names': users,
        'session_id': sessionId
    }
    updateOnServer('/api/userlist', null, data, function (respData) {
        // Since user list has been updated, force a dashboard refresh.
        angular.element($('#timing-dashboard')).scope().etaUpdate();
    });
}

function positionMapNoLocationServices() {
    $.post('https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyBhrGYLquM8Z1ENwYMbQLVueqVmjFUTs1c', {},
        function (resp) {
            map.setCenter(resp.location);
            map.setZoom(Math.max(8, Math.min(11, (20 - Math.round(Math.log(resp.accuracy / 1125))))));
        });
}

function selectCurrLoc() {

    var currLoc = new google.maps.LatLng(current_lat, current_long);

    var service = new google.maps.Geocoder();
    var request = {
        'location': currLoc
    }

    service.geocode(request, function (results, status) {

        prepareMapAndTimeElements(results[0]['place_id'], function (newPlace) {

            updateTimes(newPlace);
            createSession(function () {

                if (ugsId) {
                    refreshEta();
                }
                else {
                    angular.element($('#timing-dashboard')).scope().etaUpdate();
                }
            }, newPlace);
        });

    });
}

function enableDashboard(force) {
    //If dashboard is enabled, Destination Panel should be enabled.
    enableDestinationPanel();
    $('#timing-dashboard').show();
    //$('#dashboard-tab-picker').parent().css('display', 'block');
    $('#tagline-text').addClass('hidden-xs');

    //Temporarily short-circuiting this. Now it enables the deststuff / 'me' panel
    if (userMode == 'REQUESTER' || userMode == 'VIEWER') {
        $('#timing-dashboard').show();
        $('#dashboard-tab-picker').parent().css('display', 'block');
    }
    else if (userMode == 'SHARER') {

        //This is the person providing the updates.
        enableDestStuff()

        // If there is anyone other than this user in the UGS list,
        // the dashboard should be shown.
        if (force) {
            $('#dashboard-tab-picker').parent().css('display', 'block');
        }
    }
}

function enableDestStuff() {
    if (!WURFL.is_mobile) {
        // We don't support joining sessions on desktop.
        return;
    }
    $('#join-panel').show();
    $('#deststuff-tab-picker').parent().css('display', 'block');
}

function showDashboard() {
    enableDashboard();

    //TEMPORARILY DISABLE. Some cases will want to go to DestStuff.
    // If there is a UGS associated with this GS, then switch here.

    ////Switch view here.
    if (userMode != 'SHARER') {
        $('#dashboard-tab-picker').tab('show');
    }
}

function hideDashboard() {
    $('#dashboard-tab-picker').parent().css('display', 'none');
}

function showDestStuff() {
    enableDestStuff();
    //Switch view here.
    if (userMode != 'UNKNOWN') {
        $('#deststuff-tab-picker').tab('show');
    }
}

function enableDestinationPanel() {
    //$('#planning-tab').show()
    if (userMode == 'SHARER') {
        $('#use-your-location').hide();
        if (!destinationSet) {
            $('#banner-headline').text('Save your friend some time.');
        }
    }
    $('#planning-tab-picker').parent().css('display', 'block');
    //google.maps.event.trigger(map,'resize');
    destPanelEnabled = true;
}

function hideDestinationPanel() {
    $('#planning-tab-picker').parent().css('display', 'none');
}

function showDestinationPanel() {
    if (!destPanelEnabled) {
        enableDestinationPanel();
    }
    $('#planning-tab-picker').tab('show');
    if (!destPanelEnabled) {
        google.maps.event.trigger(map, 'resize');
    }
}