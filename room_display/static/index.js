angular.module('roomDisplayApp', [])
  .controller('RoomDisplayController', function() {
    var roomDisplay = this;
    roomDisplay.rooms = [
        {name: 'A room'},
        {name: 'Another room'}
    ];
});
