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
            data: `{"x":${x}, "y":${y}}`,
            beforeSend: api.augmentRequestWithCSRFToken,
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

    /* Creates a new movable view.
     */
    function createMovableView( movable )
    {
        const movableView = $( '#movable-template' ).clone();
        movableView.appendTo( $( '#movables-view .movables-list' ) );
        movableView.attr( 'id', '' );
        movableView.attr( 'url', movable.url );
        movableView.find( '.movable-name' ).text( '★ ' + movable.name );
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

        const shipTemplate = movableView.find( '#ship-template' ).clone();
        for( const ship of movable.ship_set )
        {
            const shipView = shipTemplate.clone();
            shipView.attr( 'id', '' );
            shipView.appendTo( movableView.find( '.ship-list' ) );
            shipView.text( ship.blueprint.data.name );
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
        if( JSON.stringify( movable.destination ) == JSON.stringify( movable.position ) )
        {
            movableView.find( '.movable-status' ).text( 'Standing by.' );
        }
        else
        {
            movableView.find( '.movable-status' ).html( '&nbsp;' );
            $.get( movable.process,
                function( process )
                {
                    const destination = world.getHexField( movable.destination[ 0 ], movable.destination[ 1 ] ).attr( 'name' );
                    var turns = process.end_tick - world.game.tick;
                    turns = turns == 1 ? `${ turns } turn` : `${ turns } turns`;
                    movableView.find( '.movable-status' ).html( `<span class="movable-status-line">Heading to <b>${ destination }</b>.</span> <span class="movable-status-line">Next jump in <b>${ turns }</b>.</span>` );
                }
            );
        }
    }

    /* Load the content.
     */
    $( document ).ready( function()
    {
        if( $( '#movables-view' ).length )
        {
            $( '#movables-view' ).hide();
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

                    $( '#movables-view' ).fadeIn( 200 );
                }
                else
                {
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
