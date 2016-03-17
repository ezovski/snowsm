/**
 * Created by mattezovski on 7/13/15.
 */

var updateFrequency = 60000;

var etaDashboard = angular.module('etaDashboard', ['ui.bootstrap', 'ngAnimate']);

etaDashboard.controller('EtaListCtrl', function($scope, $http) {

    $scope.setUserId = function ($event, userId) {
        $event.preventDefault();
        switchToDiffUser(userId);
    };

    $scope.userUpdates = [];

    $scope.isMobile = WURFL.is_mobile;

    $scope.updateTimerActive = false;
    $scope.panelOpen = 0;

    $scope.setOpenUser = function (indexOfUser) {

        if ($scope.panelOpen != null) {
            $scope.userUpdates[$scope.panelOpen]['openInDashboard'] = false;
        }

        $scope.panelOpen = (indexOfUser == $scope.panelOpen) ? null : indexOfUser;
        if ($scope.panelOpen != null) {
            $scope.userUpdates[$scope.panelOpen]['openInDashboard'] = true;
        }


    }

    $scope.scheduleDashboardUpdate = function () {

        if (!$scope.updateTimerActive) {
            $scope.updateTimerActive = true;
        }
        else {
            // Trigger a location update if we have departed.
            if (ugsId) {
                updateLocation(refreshEta);
            }
            else {
                $scope.etaUpdate();
            }
        }
        window.setTimeout($scope.scheduleDashboardUpdate, updateFrequency);

    }

    $scope.etaUpdate = function() {

        //Show dashboard div
        enableDashboard();

        //httpGet the current status for the whole session
        getEtasForSession(sessionId,function(respData){
            $scope.userUpdates = respData['objects'];
            if ($scope.userUpdates.length) {
                if (userMode == 'UNKNOWN') {
                    userMode = 'VIEWER';
                    // Switch to status tab.
                    showDashboard();
                }
            }
            else if (userMode == 'UNKNOWN') {
                // User is a potential sharer. Use that mode.
                userMode = 'SHARER';
                showDestStuff();
                hideDestinationPanel();

            }
            for (var i=0; i < $scope.userUpdates.length; i++) {
                var u = $scope.userUpdates[i];

                switch (u['status']) {
                    case 'NEEDS_DEST':
                        u['arrival_time'] = 'Needs Destination';
                        break;
                    case 'IN_TRANSIT':
                    case 'IS_GOING':
                        if (u.last_eta) {
                            u['arrival_time'] = convertTimestampToLocalTime(u.last_eta);
                        }
                        else {
                            u['arrival_time'] = 'ON TIME';
                        }
                        break;
                    case 'NEARBY':
                        u['arrival_time'] = 'NEARBY';
                        break;
                    case 'ARRIVED_PRESUMED':
                        u['arrival_time'] = 'PROBABLY ARRIVED';
                    case 'ARRIVED':
                        u['arrival_time'] = 'ARRIVED';
                        break;
                    case 'CANCELED':
                        u['arrival_time'] = 'BACKED OUT';
                        break;
                    default:
                        u['arrival_time'] = 'UNKNOWN';
                        break;
                }

                // Set a flag if this is the current user's ugs.
                if (currentUserId && currentUserId == u.user_id) {
                    u['is_current_user'] = true;
                }
                else {
                    u['is_current_user'] = false;
                    enableDashboard(true);
                }

                if (u.last_eta_updated) {
                    u['last_eta_updated'] = convertTimestampToLocalTime(u.last_eta_updated);
                }

            }

            // Set appropriate row of dashboard to be open.
            if ($scope.panelOpen != null && $scope.userUpdates.length > $scope.panelOpen) {
                $scope.userUpdates[$scope.panelOpen]['openInDashboard'] = true;
            }

            $scope.$apply();
            setSelfArrivalTimeFromUgsList($scope.userUpdates);

            if (!$scope.updateTimerActive) {
                $scope.scheduleDashboardUpdate();
            }

            return;
        });

    }
});

etaDashboard.controller('TimeListCtrl', function ($scope) {

    $scope.userTime = null;
    $scope.times = [];
    var x = 0;
    var interval = 15;
    var funTimes = _.range(0, 1440, interval);
    var zone = (new Date()).getTimezoneOffset() / 60;

    for (var i = 0; i < 1440 / interval; i++) {
        var newOption = {};
        var hour = (Math.floor(funTimes[i] / 60) + zone) % 24;
        var hourTemp = Math.floor(funTimes[i] / 60);
        var hourFormatted = hourTemp % 12;
        if (hourFormatted == 0) {
            hourFormatted = 12;
        }
        var minutesStr = funTimes[i] % 60;
        if (minutesStr == '0') {
            minutesStr = '00';
        }
        var amPm = hourTemp < 12 ? ' AM' : ' PM';
        var hourStr = hour.toString();
        if (hourStr.length == 1) {
            hourStr = '0' + hourStr;
        }
        newOption['value'] = hourStr + ':' + minutesStr;
        newOption['text'] = hourFormatted.toString() + ':' + minutesStr + amPm;
        $scope.times.push(newOption);
    }

    $scope.timeChange = function () {

        // We're now in Manual mode.
        ugsRefreshMode = 'MANUAL';
        ugsStatus = 'IS_GOING';
        // Update the associated UGS.
        if (sessionId) {
            refreshEta();
        }
        else {
            createSession(refreshEta);
        }
        // When result returns, show brief alert.

    };

    $scope.setEtaDefault = function () {

        if (!$scope.userTime) {
            var d = new Date();
            var output = '';
            var hours = (d.getUTCHours() + 1) % 24;
            if (hours < 10) {
                output = '0';
            }

            $scope.userTime = output.concat(hours.toString()).concat(':00');
            $scope.timeChange();
        }

    };

});

etaDashboard.controller('MobileOnlyTextCtrl', function ($scope) {

    $scope.isMobile = WURFL.is_mobile;

});
