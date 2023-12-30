function world( api, hexFieldSize = 200 )
{
    const hexScaleFactor = 1 - 4 / 104; // overlap borders of adjacent fields

    /* Returns the pixel coordinates of a hex field given in hex grid coordinates.
     */
    function getHexX( x )
    {
        return x * hexFieldSize * hexScaleFactor / 2;
    }
    function getHexY( y )
    {
        return y * hexFieldSize * 0.75 * hexScaleFactor;
    }

    /* Creates a new hex field at the specified hex grid coordinates.
     */
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
        hexField.css({
            left: getHexX( x ), top: getHexY( y )
        });
        return hexField;
    }

    /* Centers the hex map upon the hex field specified in hex grid coordinates.
     */
    function centerMap( x, y )
    {
        $( '#hex-map' ).attr( 'x', $( '#hex-map-container' ). width() / 2 - getHexX( x ) - hexFieldSize / 2 );
        $( '#hex-map' ).attr( 'y', $( '#hex-map-container' ).height() / 2 - getHexY( y ) - hexFieldSize / 2 );
        updateMap();
    }

    /* Updates the view of the hex map after changing its position.
     */
    function updateMap()
    {
        $( '#hex-map' ).css( 'left', $( '#hex-map' ).attr( 'x' ) );
        $( '#hex-map' ).css(  'top', $( '#hex-map' ).attr( 'y' ) );
    }

    /* Loads the map.
     */
    function loadMap()
    {
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
                updateMap();
    
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
    
        $.get( api.url + '/unveiled', function( data )
        {
            for( const unveiled of data )
            {
                createHexField( unveiled.position[0], unveiled.position[1] );
            }
        });
        $.get( api.url + '/sectors', function( data )
        {
            for( const sector of data )
            {
                const hexField = getHexField( sector.position[0], sector.position[1] );
                hexField.find( '.sector-name' ).text( sector.name );
            }
        });
    }

    /* Returns the hex field at the specified hex grid coordinates.
     */
    function getHexField( x, y )
    {
        return $( `.hex-field a[x="${ x }"][y="${ y }"]` ).parent().parent();
    }

    /* Load the map and center the view upon the home world.
     */
    $( document ).ready( function()
    {
        if( $( '#hex-map' ).length )
        {
            loadMap();
        
            $.get( api.url + '/users', function( users )
            {
                $.get( users[0].empire, function( empire )
                {
                    $.get( empire.habitat[0], function( celestial )
                    {
                        $.get( celestial.sector, function( sector )
                        {
                            centerMap( sector.position[0], sector.position[1] );
                        });
                    });
                });
            });
        }
    });

    return
    {
        centerMap: centerMap
    };
}
