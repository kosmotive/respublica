const api = 'http://127.0.0.1:8000/api';
const hexFieldSize = 200;


function createHexField( x, y )
{
    const hexField = $( '#hex-field-template' ).clone();
    hexField.appendTo( '#hex-map' );
    hexField.attr( 'id', '' );
    hexField.find('a').attr( 'x', x );
    hexField.find('a').attr( 'y', y );
    hexField.find('a').click( function()
    {
        console.log('clicked: ' + this.getAttribute('x') + ', ' + this.getAttribute('y'));
    });
    const scaleFactor = 1 - 4 / 104; // overlap borders of adjacent fields
    const pxX = x * hexFieldSize * scaleFactor / 2;
    const pxY = y * hexFieldSize * 0.75 * scaleFactor;
    hexField.css({
        left: pxX, top: pxY
    });
    hexField.data( 'center', function()
    {
        $( '#hex-map' ).attr( 'x', -pxX + $( '#hex-map-container' ). width() / 2 -  hexField.width() / 2 );
        $( '#hex-map' ).attr( 'y', -pxY + $( '#hex-map-container' ).height() / 2 - hexField.height() / 2 );
        $( '#hex-map' ).data( 'updatePosition' ).call( $( '#hex-map' )[0] );
    });
    return hexField;
}


function loadMap()
{
    $( '#hex-map' ).data( 'updatePosition', function()
    {
        $( this ).css( 'left', this.getAttribute( 'x' ) );
        $( this ).css(  'top', this.getAttribute( 'y' ) );
    });

    var initialX = null, initialY = null; // the coordinates of the mouse when dragging started
    var offsetX = null; offsetY = null; // the offset of the map before dragging started
    var dragging = false; // indicates whether the mouse was pressed *on the map* and not somewhere else
    $( '#hex-map' ).on
    ({
        mousemove: function( event )
        {
            if( event.buttons != 1 || !dragging )
            {
                dragging = false;
                return;
            }

            this.setAttribute( 'x', offsetX + event.clientX - initialX );
            this.setAttribute( 'y', offsetY + event.clientY - initialY );
            $( this ).data( 'updatePosition' ).call( this );

            event.preventDefault();
        },
        mousedown: function( event )
        {
            dragging = true;

            initialX = event.clientX;
            initialY = event.clientY;

            offsetX = parseInt(this.getAttribute( 'x' ));
            offsetY = parseInt(this.getAttribute( 'y' ));
        }
    });

    $.get( api + '/unveiled', function( data )
    {
        for( const unveiled of data )
        {
            createHexField( unveiled.position[0], unveiled.position[1] );
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
    
        $.get( api + '/users', function( users )
        {
            $.get( users[0].empire, function( empire )
            {
                $.get( empire.habitat[0], function( celestial )
                {
                    $.get( celestial.sector, function( sector )
                    {
                        const hexField = $( `.hex-field a[x="${ sector.position[0] }"][y="${ sector.position[1] }"]` ).parent().parent();
                        hexField.data( 'center' )();
                    });
                });
            });
        });
    }
});
