function world( api, blueprints, hexFieldSize = 200 )
{
    const hexScaleFactor = 1 - 4 / 104; // overlap borders of adjacent fields
    const movables = {};
    const status = {};
    const empires = {};
    const events =
    {
        /* Fired when a hex field is cliked (x, y, sectorUrl).
         */
        hex_field_click: new CallbackStack()
    };

    var clickableMap = false; // indicates whether click events on #hex-map should be treated as map clicks

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
            if( !clickableMap ) return;

            const x = parseInt( this.getAttribute( 'x' ) );
            const y = parseInt( this.getAttribute( 'y' ) );

            const hexField = getHexField( x, y );
            events.hex_field_click.fire( x, y, hexField.attr( 'sector' ) );
        });
        hexField.css({
            left: getHexX( x ), top: getHexY( y )
        });
        hexField.find( '.sector-star ').css( 'display', 'none' );

        const movables = getMovables( x, y );
        for( const movable of movables )
        {
            $( `<li class="movable">★ ${ movable.name }</li>` ).appendTo( hexField.find('.hex-field-movables') );
        }

        const owners = getHexOwners( x, y );
        if( owners.length )
        {
            hexField.find( '.hex-field-hatch' ).attr( 'stroke', 'dodgerblue' );
        }

        return hexField;
    }

    /* Load all movables.
     */
    const loadMovables = $.get( api.url + '/movables?depth=1', function( data )
    {
        for( const movable of data )
        {
            const key = `x=${movable.position[0]} y=${movable.position[1]}`;
            if( !movables[key] ) movables[key] = [];
            movables[key].push( movable );

            for( const ship of movable.ship_set )
            {
                blueprints.require( ship.blueprint );
            }
        }
    });

    /* Encodes hex coordinates into string (required for inclusion testing in javascript).
     */
    function hex2str( x, y )
    {
        return `x=${x} y=${y}`;
    }

    /* Returns movables at specified position in hex coordinates.
     */
    function getMovables( x, y )
    {
        const key = hex2str( x, y);
        return movables[key] || [];
    };

    /* Centers the hex map upon the hex field specified in hex grid coordinates.
     */
    function centerMap( x, y )
    {
        $( '#hex-map' ).attr( 'x', Math.round( $( '#hex-map-container' ). width() / 2 - getHexX( x ) - hexFieldSize / 2 ) );
        $( '#hex-map' ).attr( 'y', Math.round( $( '#hex-map-container' ).height() / 2 - getHexY( y ) - hexFieldSize / 2 ) );
        updateMap();
    }

    /* Updates the view of the hex map after changing its position.
     */
    function updateMap()
    {
        $( '#hex-map' ).css( 'left', $( '#hex-map' ).attr( 'x' ) );
        $( '#hex-map' ).css(  'top', $( '#hex-map' ).attr( 'y' ) );
    }

    /* Updates the view of a hex field after changing its name.
     */
    function updateHexField( hexField )
    {
        hexField.find( '.hex-field-name' ).text( hexField.attr( 'name' ) );
    }

    /* Loads the map (with *displayed* coordiantes centered at `origin`).
     */
    function loadMap( origin )
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
    
                this.setAttribute( 'x', Math.round( offsetX + event.clientX - initialX ) );
                this.setAttribute( 'y', Math.round( offsetY + event.clientY - initialY ) );
                updateMap();

                clickableMap = false;
                event.preventDefault();
            },
            mousedown: function( event )
            {
                dragging = true;
                clickableMap = true;
                event.preventDefault();
    
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
                const x = unveiled.position[ 0 ], y = unveiled.position[ 1 ];
                const hexField = createHexField( x, y );
                function fmt( z, negativePrefix, positivePrefix )
                {
                    if( z < 0 ) return `${ negativePrefix }${ -z }`;
                    if( z > 0 ) return `${ positivePrefix }${  z }`;
                    else return '0';
                }
                hexField.attr( 'name', `${ fmt( x - origin[ 0 ], "W", "E" ) }/${ fmt( y - origin[ 1 ], "N", "S" ) }` );
                updateHexField( hexField );
            }
        });
        $.get( api.url + '/sectors?depth=1', function( data )
        {
            for( const sector of data )
            {
                const hexField = getHexField( sector.position[0], sector.position[1] );
                hexField.addClass( 'sector' );
                hexField.attr( 'name', sector.name );
                hexField.attr( 'sector', sector.url );
                updateHexField( hexField );

                switch( sector.celestial_set[0].features.variant )
                {

                case 'white-mainline': 
                    hexField.find( '.sector-star-mainline .star-brush' ).attr( 'fill', 'white' );
                    hexField.find( '.sector-star-mainline' ).css( 'display', 'inline' );
                    break;

                case 'yellow-mainline': 
                    hexField.find( '.sector-star-mainline .star-brush' ).attr( 'fill', 'orange' );
                    hexField.find( '.sector-star-mainline' ).css( 'display', 'inline' );
                    break;

                case 'blue-mainline': 
                    hexField.find( '.sector-star-mainline .star-brush' ).attr( 'fill', 'dodgerblue' );
                    hexField.find( '.sector-star-mainline' ).css( 'display', 'inline' );
                    break;

                case 'white-dwarf':
                    hexField.find( '.sector-star-white-dwarf' ).css( 'display', 'inline' );
                    break;

                case 'red-giant':
                    hexField.find( '.sector-star-red-giant' ).css( 'display', 'inline' );
                    break;

                default:
                    console.log( `Unknown star variant: "${ sector.celestial_set[0].features.variant }"` );

                }
            }
        });
    }

    /* Returns the hex field at the specified hex grid coordinates.
     */
    function getHexField( x, y )
    {
        return $( `.hex-field a[x="${ x }"][y="${ y }"]` ).parent().parent();
    }

    /* Load discovered empires (territories are required for rendering the world map).
     */
    const loadEmpires = $.get( api.url + '/empires',
        function( data )
        {
            for( const empire of data )
            {
                empires[ empire.url ] = empire;
                const territory = [];
                for( c of empire.territory )
                {
                    territory.push( hex2str( c[ 0 ], c[ 1 ] ) );
                }
                empire.territory = territory;
            }
        }
    );

    /* Get owners of a hex field (by hex coordinates).
     */
    function getHexOwners( x, y )
    {
        owners = [];
        for( const empire of Object.values( empires ) )
        {
            if( empire.territory.includes( hex2str( x, y ) ) )
            {
                owners.push( empire );
            }
        }
        return owners;
    }

    /* Resolve blueprints and load the world content.
     */
    $.when( loadMovables, loadEmpires ).done(
        function()
        {
            blueprints.resolve();
            blueprints.whenResolved(
                function()
                {
                    /* Update the required blueprints with the resolved data.
                     */
                    for( const movablesList of Object.values( movables ) )
                    {
                        for( const movable of movablesList )
                        {
                            for( const ship of movable.ship_set )
                            {
                                ship.blueprint = blueprints.get( ship.blueprint );
                            }
                        }
                    }

                    /* Load the content.
                     */
                    $( document ).ready(
                        function()
                        {
                            if( $( '#hex-map' ).length )
                            {
                                $( '#hex-map-container' ).hide();
                                $.get( api.url + '/users', function( users )
                                {
                                    $.get( users[0].empire, function( empire )
                                    {
                                        /* Load the map.
                                         */ 
                                        loadMap( empire.origin );

                                        /* Center the map upon the home world (if no explicit coordinates are given in URL).
                                         */
                                        const mapPosition = window.location.hash.substr(1).split(',')
                                        if( mapPosition.length == 2 )
                                        {
                                            $( '#hex-map' ).attr( 'x', mapPosition[ 0 ] );
                                            $( '#hex-map' ).attr( 'y', mapPosition[ 1 ] );
                                            updateMap();
                                        }
                                        else
                                        {
                                            centerMap( empire.origin[ 0 ], empire.origin[ 1 ] );
                                        }

                                        /* Show the map.
                                         */
                                        $( '#hex-map-container' ).fadeIn( 200 );
                                    });
                                });
                            } // if( $( '#hex-map' ).length )
                        }
                    ); // $( document ).ready
                }
            ); // blueprints.whenResolved
        }
    );

    /* Update displays according to game status.
     */
    $( document ).ready( function()
    {
        $.get( api.url + '/worlds', function( worlds )
        {
            var remainingSeconds = worlds[0].remaining_seconds
            const updateRemainingSeconds = function()
            {
                var remainingTime;

                if( remainingSeconds <= 60 )
                    remainingTime = `${ remainingSeconds } seconds`
                else
                if( remainingSeconds <= 60 * 60 )
                    remainingTime = `${ Math.floor( remainingSeconds / 60 ) } minutes`
                else
                    remainingTime = `${ Math.floor( remainingSeconds / ( 60 * 60 ) ) } hours`

                if( remainingSeconds >= 0 )
                {
                    $(' #remaining-time ').text( remainingTime );
                    --remainingSeconds;
                }
                else
                {
                    clearTimeout( updateRemainingSeconds );
                    const x = $( '#hex-map' ).attr( 'x' ), y = $( '#hex-map' ).attr( 'y' );
                    window.location.hash = `${ x },${ y }`;
                    location.reload();
                }
            };

            $(' #ticks ').text( worlds[0].now );
            status.tick = worlds[0].now;

            updateRemainingSeconds();
            const remainingTimer = setInterval( updateRemainingSeconds, 1000 );
        });
    });

    const ret =
    {
        events: events,
        centerMap: centerMap,
        movables: movables,
        getMovables: getMovables,
        status: status,
        empires: empires,
        getHexField: getHexField
    };
    return ret;
}
