var roomDisplayModule = angular.module('roomDisplayApp', []);

roomDisplayModule.config(function($provide) {
    $provide.factory('$roomData', function($http, $interval) {
        var roomDataInstance = {};

        // Object structure is updated by polling
        roomDataInstance.roomData = {};
        // Make it available as a list for the UI
        roomDataInstance.rooms = [];


        /*
            Util functions
        */
        roomDataInstance.currentTimeMinutes = function() {
            var now = new Date();
            return (now.getHours() * 60) + now.getMinutes();
        };

        roomDataInstance.formatMinutes = function(minutes) {
            var m = minutes % 60,
                h = (minutes - m) / 60;
            return h + ':' + (m < 10 ? '0' : '') + m;
        };


        /*
            Polling functions
        */
        roomDataInstance._poll ={
            enabled: false,
            last_poll_minutes: 0,
            // Until the first server poll, assume polling minutely from midnight to midnight
            interval: 1,
            start_minute: 0,
            end_minute: 1440
        };
        roomDataInstance.enablePolling = function() {
            roomDataInstance._poll.enabled = true;
        };
        roomDataInstance.disablePolling = function() {
            roomDataInstance._poll.enabled = false;
        };
        $interval(function() {
            if (roomDataInstance._poll.enabled) {
                roomDataInstance.update();
            }
        }, 1000);


        /*
            Update functions
        */
        roomDataInstance.update = function() {
            var current_minutes = roomDataInstance.currentTimeMinutes();

            if (current_minutes < roomDataInstance._poll.last_poll_minutes) {
                // Gone over a day boundary; reset last polled time
                roomDataInstance._poll.last_poll_minutes = 0;
            }

            var next_poll = roomDataInstance._poll.last_poll_minutes + roomDataInstance._poll.interval,
                poll_now = (
                    // We're within polling time bounds
                    current_minutes > roomDataInstance._poll.start_minute
                    && current_minutes < roomDataInstance._poll.end_minute
                    // We've waited long enough
                    && current_minutes > next_poll
                );

            if (poll_now) {
                // It's pollin' time!
                roomDataInstance.updateNow();
            }
        };

        roomDataInstance.updateNow = function() {
            $http
                .get('/data')
                .then(function(response) {
                    roomDataInstance.parseData(response.data);
                });
            // TODO: Error handling
        };

        roomDataInstance.parseData = function(data) {
            roomDataInstance._updatePoll(data.polling);
            roomDataInstance._updateRooms(data.rooms);
            roomDataInstance._updateRoomList();
        };

        roomDataInstance._updatePoll = function(data) {
            // Update polling setup
            roomDataInstance._poll.interval = data.interval || roomDataInstance._poll.interval;
            roomDataInstance._poll.start_minute = data.start_minute || roomDataInstance._poll.start_minute;
            roomDataInstance._poll.end_minute = data.end_minute || roomDataInstance._poll.end_minute;
            roomDataInstance._poll.last_poll_minutes = roomDataInstance.currentTimeMinutes();
        };

        roomDataInstance._updateRooms = function(data) {
            // Get room data into dictionary structure to make updating easier
            data.forEach(function(room) {
                roomDataInstance._updateRoom(room);
                roomDataInstance._updateRoomBookings(room);
            });
        };

        roomDataInstance._updateRoom = function(room) {
            // If this is a new room, add it
            if (roomDataInstance.roomData[room.id] === undefined) {
                roomDataInstance.roomData[room.id] = {
                    bookings: []
                };
            }

            // Update the properties
            roomDataInstance.roomData[room.id].id = room.id;
            roomDataInstance.roomData[room.id].name = room.name;
            roomDataInstance.roomData[room.id].description = room.description;
        };

        roomDataInstance._updateRoomBookings = function(room) {
            // Get parsed future bookings
            var future_bookings = roomDataInstance._getFutureBookings(room.bookings)
                parsed_future_bookings = roomDataInstance._parseBookings(future_bookings);

            // Update bookings
            roomDataInstance.roomData[room.id].bookings.length = 0;
            parsed_future_bookings.forEach(function(booking) {
                roomDataInstance.roomData[room.id].bookings.push(booking);
            });
            roomDataInstance.roomData[room.id].first_booking = roomDataInstance.roomData[room.id].bookings[0];
        };

        roomDataInstance._getFutureBookings = function(data) {
            var current_minutes = roomDataInstance.currentTimeMinutes();
            return data.filter(function(booking) {
                return current_minutes < booking.end_minute;
            });
        };

        roomDataInstance._parseBookings = function(data) {
            // Assume server has sorted by start time

            // First possible free time is later of now and start of day
            var last_booked_time = Math.max(
                    roomDataInstance.currentTimeMinutes(),
                    roomDataInstance._poll.start_minute
                ),
                parsed_bookings = [];

            data.forEach(function(booking) {
                // Check if there needs to be free time before this booking
                if (last_booked_time < booking.start_minute) {
                    parsed_bookings.push({
                        available: true,
                        start_minute: last_booked_time,
                        end_minute: booking.start_minute
                    });
                }
                last_booked_time = booking.end_minute;

                booking.available = false;
                parsed_bookings.push(booking);
            });

            // Add free time after the last meeting of the day?
            if (last_booked_time < roomDataInstance._poll.end_minute) {
                parsed_bookings.push({
                    available: true,
                    start_minute: last_booked_time,
                    end_minute: roomDataInstance._poll.end_minute
                });
            }

            // Work out some extra stuff
            var now = roomDataInstance.currentTimeMinutes();
            parsed_bookings.forEach(function(booking) {
                booking.start_time = roomDataInstance.formatMinutes(booking.start_minute);
                booking.end_time = roomDataInstance.formatMinutes(booking.end_minute);
                booking.starts_in_minutes = booking.start_minute - now;
                booking.ends_in_minutes = booking.end_minute - now;
            });

            return parsed_bookings;
        };

        roomDataInstance._updateRoomList = function() {
            if (roomDataInstance.rooms.length !== 0) {
                // Room list is already setup; assume it won't change
                return;
            }

            // Add each room from roomData to the rooms list
            Object.keys(roomDataInstance.roomData).forEach(function(room_id) {
                roomDataInstance.rooms.push(roomDataInstance.roomData[room_id]);
            });

            // Order rooms list by name
            roomDataInstance.rooms.sort(function compare(r1, r2) {
                return r1.name > r2.name;
            });
        };

        return roomDataInstance;
    });
});


roomDisplayModule.controller('RoomDisplayController', function($roomData, $scope) {
    var roomDisplay = this;

    // Make the list of rooms available to the template
    roomDisplay.rooms = $roomData.rooms;

    $roomData.enablePolling();
    //$roomData.update();
});


roomDisplayModule.controller('TimeController', function($scope, $interval) {
    // Ticking Clock
    // http://stackoverflow.com/questions/23383233/how-to-make-a-ticking-clock-time-in-angularjs-and-html
    var tick = function() {
        $scope.clock = Date.now();
    }
    tick();
    $interval(tick, 1000);
});


// Fullscreen button
document.getElementById('fullscreen').onclick = function() {
    var req = document.body.requestFullScreen || document.body.webkitRequestFullScreen || document.body.mozRequestFullScreen;
    req.call(document.body.parentNode);
};


// Show the page name in the dropdown
$('#page_changer').on('hidden.bs.dropdown', update_page_name);

function update_page_name() {
    var page_name = $('#page_changer li.active').text();
    $('#page_name').text(page_name);
}

$(document).ready(function() {
    //Show the current page name
    update_page_name();
});
