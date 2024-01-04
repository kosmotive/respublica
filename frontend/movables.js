function movables( api, world )
{
    var selectedMovable = null;
    const events =
    {
    };

    /* Dispatch "move_to" action for the selected movable (if any).
     */
    function moveTo( x, y )
    {
        if( !selectedMovable ) return true;
        $.ajax({
            type: 'POST',
            url: selectedMovable.url + 'move_to/',
            contentType: 'application/json',
            data: `{"x": ${ x }, "y": ${ y }}`,
            beforeSend: api.augmentRequestWithCSRFToken,
            ignore403: true,
            success: function( data )
            {
                delete data.ship_set;
                Object.assign( selectedMovable, data );
                updateMovableView( selectedMovable );
                world.showTrajectory( selectedMovable );
            }
        });
        $( `#movables-view .movable[url="${ selectedMovable.url }"] .action-move` ).trigger( 'click' );
        return false;
    }

    /* Dispatch "colonize" action for the selected movable (if any).
     */
    function colonize( celestial )
    {
        if( !selectedMovable ) return;
        $.ajax({
            type: 'POST',
            url: celestial.url + 'colonialize/',
            contentType: 'application/json',
            data: `{"movable": "${ selectedMovable.url }"}`,
            beforeSend: api.augmentRequestWithCSRFToken,
            ignore403: true,
            success: function( data )
            {
                delete data.ship_set;
                Object.assign( selectedMovable, data );
                updateMovableView( selectedMovable );
                world.showTrajectory( selectedMovable );
            }
        });
    }

    /* Creates a new movable view.
     */
    function createMovableView( movable )
    {
        const color = world.empires[ movable.owner ].color;
        const movableView = $( '#movable-template' ).clone();
        movableView.appendTo( $( '#movables-view .movables-list' ) );
        movableView.attr( 'id', '' );
        movableView.attr( 'url', movable.url );
        movableView.find( '.movable-name' ).text( movable.name );
        movableView.css( 'border-color', color );
        movableView.find( '.movable-icon' ).css( 'background-color', color );
        if( movable.owner == world.game.empire.url )
        {
            /* Select the movable on click.
             */
            movableView.on( 'click',
                function()
                {
                    if( selectedMovable && selectedMovable.url == movable.url ) return;
                    $( '#movables-view .movables-list .movable-active' ).removeClass( 'movable-active' );
                    movableView.addClass( 'movable-active' );
                    selectedMovable = movable;
                    world.showTrajectory( selectedMovable );
                }
            );

            /* Activate movement mode when "Move" button is clicked.
             */
            movableView.find( '.action-move' ).on( 'click',
                function()
                {
                    if( $( this ).hasClass( 'action-toggled' ) )
                    {
                        $( this ).removeClass( 'action-toggled' );
                        world.events.hex_field_click.pop( moveTo );
                    }
                    else
                    {
                        $( this ).addClass( 'action-toggled' );
                        world.events.hex_field_click.push( moveTo );
                    }
                }
            );

            /* Check whether a colony-ship is included.
             */
            if( movable.ship_set.some( ( ship ) => { return ship.type_id == 'ships/colony-ship'; } ) )
            {
                /* Check whether the sector contains a celestial suitable for colonialization.
                 */
                const sector = world.getSector( movable.position[ 0 ], movable.position[ 1 ] );
                if( sector )
                {
                    const isUnhabitated = sector.celestial_set.every( ( c ) => { return c.habitated_by === null; } );
                    const habitableCelestials = sector.celestial_set.filter( ( c ) => { return c.features.capacity > 0; } );
                    if( isUnhabitated && habitableCelestials.length )
                    {
                        /* Build menu of available celestials for colonialization.
                         */
                        const celestialMenu = movableView.find( '.action-colonialize .popup' );
                        movableView.addClass( 'can-colonialize' );
                        celestialMenu.find( '.action-list' ).empty();
                        for( const celestial of habitableCelestials )
                        {
                            const action = $( `<li class="action">${ world.getCelestialName( sector, celestial ) }</li>` );
                            action.appendTo( celestialMenu.find( '.action-list' ) );
                            action.on( 'click',
                                function()
                                {
                                    colonize( celestial );
                                }
                            );
                        }

                        /* Show the menu.
                         */
                        movableView.find( '.action-colonialize' ).on( 'click',
                            function()
                            {
                                celestialMenu.popup();
                            }
                        );
                    }
                }
            }
        }
        else
        {
            movableView.addClass( 'foreign' );
        }

        const shipTemplate = movableView.find( '#ship-template' ).clone();
        for( const ship of movable.ship_set )
        {
            const shipView = shipTemplate.clone();
            shipView.attr( 'id', '' );
            shipView.appendTo( movableView.find( '.ship-list' ) );
            shipView.text( ship.type );
        }
        shipTemplate.remove();

        updateMovableView( movable );
        return movableView;
    }

    /* Update the movable view.
     */
    function updateMovableView( movable )
    {
        const movableView = $( `.movable[url="${ movable.url }"]` );
        if( movable.process )
        {
            movableView.find( '.movable-status' ).html( '&nbsp;' );
            $.get( movable.process,
                function( process )
                {
                    var turns = process.end_tick - world.game.tick;
                    turns = turns == 1 ? `${ turns } turn` : `${ turns } turns`;

                    switch( process.handler_id )
                    {

                    case 'MovementHandler':
                        const destination = world.getHexField( movable.destination[ 0 ], movable.destination[ 1 ] ).attr( 'name' );
                        movableView.find( '.movable-status' ).html( `<span class="movable-status-line">Heading to <b>${ destination }</b>.</span> <span class="movable-status-line">Next jump in <b>${ turns }</b>.</span>` );
                        break;

                    case 'ColonializationHandler':
                        const sector = world.getSector( movable.position[ 0 ], movable.position[ 1 ] );
                        const celestial = sector.celestial_set.find( ( c ) => { return c.url == process.data.celestial_url; } );
                        const celestialName = world.getCelestialName( sector, celestial );
                        movableView.find( '.movable-status' ).html( `<span class="movable-status-line">Colonizing <b>${ celestialName }</b></span> <span class="movable-status-line">in <b>${ turns }</b>.</span>` );
                        break;

                    default:
                        console.log( `Unknown process handler: "${ process.handler_id }"` );

                    }
                }
            );
        }
        else
        {
            movableView.find( '.movable-status' ).text( 'Standing by.' );
        }
    }

    /* Load the content.
     */
    $( document ).ready( function()
    {
        if( $( '#movables-view' ).length )
        {
            world.events.hex_field_click.push( function( x, y, sectorUrl )
            {
                selectedMovable = null;
                world.showTrajectory( selectedMovable );
                world.selectHexField( x, y );

                /* Show or hide the sector view, depending on whether the clicked hex contains movables
                 */
                const movables = world.getMovables( x, y );
                if( movables.length )
                {
                    $( '#movables-view .movable:not(#movable-template)' ).remove();

                    for( const movable of movables )
                    {
                        createMovableView( movable );
                    }

                    $( '#movables-view' ).fadeIn( 200, function()
                        {
                            $( 'body' ).addClass( 'open-movables-view' );
                        }
                    );
                }
                else
                {
                    $( 'body' ).removeClass( 'open-movables-view' );
                    $( '#movables-view' ).fadeOut( 200 );
                }
                return true;
            });
        }
    })

    const ret =
    {
        events: events
    };
    return ret;
}
