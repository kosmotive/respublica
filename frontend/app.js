const api = 'http://127.0.0.1:8000/api';
const hexFieldSize = 200;

function createHexField(x, y) {
    const hexField = $('#hex-field-template').clone();
    hexField.appendTo('#hex-map');
    hexField.attr('id', '');
    const scaleFactor = 1 - 4 / 104; // overlap borders of adjacent fields
    hexField.css({
        left: x * hexFieldSize * scaleFactor / 2, top: y * hexFieldSize * 0.75 * scaleFactor
    });
    return hexField;
}

function loadMap() {
    createHexField(0, 0);
    createHexField(2, 0);
    createHexField(4, 0);
    createHexField(1, 1);
    createHexField(3, 1);
    createHexField(2, 2);
}

$( document ).ready(function() {
    loadMap();

    $.get(api + '/users', function(data, status) {
        console.log(status);
        console.log(data);
    });
});
