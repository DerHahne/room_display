angular.module('roomDisplayApp', [])
  .controller('RoomDisplayController', function() {
    var roomDisplay = this;
    roomDisplay.rooms = [
        {name: 'A room'},
        {name: 'Another room'}
    ];
});


document.getElementById('fullscreen').onclick = function() {
    var req = document.body.requestFullScreen || document.body.webkitRequestFullScreen || document.body.mozRequestFullScreen;
    req.call(document.body.parentNode);
};
