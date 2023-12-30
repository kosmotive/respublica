const api = 'http://127.0.0.1:8000/api';
const hexFieldSize = 200;

function createHexField( x, y )
{
    const hexField = $( '#hex-field-template' ).clone();
    hexField.appendTo( '#hex-map' );
    hexField.attr( 'id', '' );
    const scaleFactor = 1 - 4 / 104; // overlap borders of adjacent fields
    hexField.css({
        left: x * hexFieldSize * scaleFactor / 2, top: y * hexFieldSize * 0.75 * scaleFactor
    });
    return hexField;
}

function loadMap()
{
    $.get({
        url: api + '/unveiled',
        success: function( data )
        {
            for( const unveiled of data )
            {
                createHexField( unveiled.position[0], unveiled.position[1] );
            }
        }
    });
}

$( document ).ajaxError( function( event, jqXHR, settings, thrownError )
{
    switch( jqXHR.status )
    {
        case 403:
            location.href = 'login.html';
            break;

        default:
            console.log('Error ' + jqHXR.status);

    }
});

$( document ).ready( function()
{
    $( '#login' ).on( 'submit', function( event )
    {
        event.preventDefault();

        $.ajax({
            type: 'POST',
            url: api + $( '#login' ).attr('action'),
            data: $( '#login' ).serialize(),
            statusCode:
            {
                400: function( data )
                {
                    console.log( data.responseJSON );
                    for( const [key, value] of Object.entries( data.responseJSON ) )
                    {
                        $( '#login-' + key + ' p' ).text( value );
                    }
                }
            },
            success: function( data )
            {
                $( '#login p.error' ).text( '' );
                location.href = 'index.html';
            }
        });
    });
    
    if( $( '#hex-map' ).length )
    {

        loadMap();
    
        $.get({
            url: api + '/users',
            success: function( data )
            {
                console.log( data[0].empire );
            }
        });
    }
});
