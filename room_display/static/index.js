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

        roomDataInstance.toFuzzyTime = function(minutes) {
            var hours = Math.floor(minutes / 60),
                remaining_minutes = minutes - (60 * hours);

            var ret = 'around '
            if (hours == 1) {
                ret += 'an hour and '
            } else if (hours >= 2) {
                hours = remaining_minutes >= 30 ? hours + 1 : hours
                ret += hours + ' hours'
                return ret
            }

            if (remaining_minutes <= 10) {
                ret += 'a few minutes'
            } else if (remaining_minutes <= 20) {
                ret += ret != '' ? 'a quarter' : 'a quarter of an hour'
            } else if (remaining_minutes <= 40) {
                ret += ret != '' ? 'a half' : 'half an hour'
            } else if (remaining_minutes <= 50) {
                ret += '45 minutes'
            } else {
                ret = ret ? '2 hours' : 'an hour'
            }
            return ret
        }


        /*
            Data update functions
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
            } else {
                // Check if anything (e.g. current booking) has changed
                roomDataInstance.updateRoomBookings();
            }
        };

        roomDataInstance.updateNow = function() {
            console.log('Fetching room data...');
            $http
                .get('/data_FUCK')
                .then(function(response) {
                    console.log('Parsing room data...');
                    // Parse & store the new information
                    roomDataInstance.parseData(response.data);

                    // Update the changing information
                    roomDataInstance._updateRoomBookingsNow();
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
                roomDataInstance.roomData[room.id]._all_bookings = roomDataInstance._parseBookings(room.bookings);
            });
        };

        roomDataInstance._updateRoom = function(room) {
            // If this is a new room, add it
            if (roomDataInstance.roomData[room.id] === undefined) {
                roomDataInstance.roomData[room.id] = {
                    _all_bookings: [],
                    bookings: []
                };
            }

            // Update the properties
            roomDataInstance.roomData[room.id].id = room.id;
            roomDataInstance.roomData[room.id].name = room.name;
            roomDataInstance.roomData[room.id].description = room.description;
        };

        roomDataInstance._parseBookings = function(data) {
            // Assume server has sorted by start time

            // First possible free time is later of now and start of day
            var last_booked_time = roomDataInstance._poll.start_minute,
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

            // Format some stuff nicely that doesn't change
            parsed_bookings.forEach(function(booking) {
                booking.start_time = roomDataInstance.formatMinutes(booking.start_minute);
                booking.end_time = roomDataInstance.formatMinutes(booking.end_minute);
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


        /*
            Polling functions
        */
        roomDataInstance._poll = {
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
        }, 10000);
        // Update as soon as we start
        roomDataInstance.update();


        /*
            Time update functions
        */
        roomDataInstance._last_update_minutes = 0;
        roomDataInstance.updateRoomBookings = function() {
            var current_minutes = roomDataInstance.currentTimeMinutes();

            if (roomDataInstance._last_update_minutes !== current_minutes) {
                roomDataInstance._updateRoomBookingsNow();
            }
        };

        roomDataInstance._updateRoomBookingsNow = function() {
            var current_minutes = roomDataInstance.currentTimeMinutes();

            // Record that the rooms have been updated
            roomDataInstance._last_update_minutes = current_minutes;

            // Update the rooms
            Object.keys(roomDataInstance.roomData).forEach(function(room_id) {
                var room = roomDataInstance.roomData[room_id];

                // Update the changing information for _all_bookings e.g. starts_in_minutes
                room._all_bookings.forEach(function(booking) {
                    booking.starts_in_minutes = booking.start_minute - current_minutes;
                    booking.ends_in_minutes = booking.end_minute - current_minutes;
                    booking.starts_in_minutes_fuzzy = roomDataInstance.toFuzzyTime(booking.starts_in_minutes);
                    booking.ends_in_minutes_fuzzy = roomDataInstance.toFuzzyTime(booking.ends_in_minutes);
                });

                // Update bookings to be future bookings from _all_bookings
                roomDataInstance._updateCurrentBookings(room);

                // Update the first meeting
                room.first_booking = roomDataInstance.roomData[room.id].bookings[0];
            });
        };

        roomDataInstance._updateCurrentBookings = function(room) {
            var future_bookings = room._all_bookings.filter(function(booking) {
                    return booking.ends_in_minutes >= 0;
                });
            angular.copy(future_bookings, room.bookings);
        };

        return roomDataInstance;
    });
});


roomDisplayModule.controller('RoomDisplayController', function($roomData, $scope) {
    var roomDisplay = this;

    // Make the list of rooms available to the template
    $scope.rooms = $roomData.rooms;

    $scope.clickRoom = function(room) {
        $scope.selected_room = room;
    }

    $roomData.enablePolling();
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


angular.element(document).ready(function() {
    // HACK: Need to wait for the navbar to be rendered before binding events to it
    setTimeout(init, 1000);
});

function init() {
    // Fullscreen button
    $('#fullscreen').on('click', function() {
        var req = document.body.requestFullScreen || document.body.webkitRequestFullScreen || document.body.mozRequestFullScreen;
        req.call(document.body.parentNode);
    });

}
