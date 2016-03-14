angular.module('roomDisplayApp', [])
    .controller('RoomDisplayController', function() {
        var roomDisplay = this;
        roomDisplay.rooms = [
            {name: 'A room'},
            {name: 'Another room'}
        ];
    }).controller('TimeController', function($scope, $interval) {
        // Ticking Clock
        // http://stackoverflow.com/questions/23383233/how-to-make-a-ticking-clock-time-in-angularjs-and-html
        var tick = function() {
            $scope.clock = Date.now();
        }
        tick();
        $interval(tick, 1000);
    });


// document.getElementById('fullscreen').onclick = function() {
//     var req = document.body.requestFullScreen || document.body.webkitRequestFullScreen || document.body.mozRequestFullScreen;
//     req.call(document.body.parentNode);
// };

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
