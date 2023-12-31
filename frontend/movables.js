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
            beforeSend: api.augmentRequestWithCSRFToken                
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
        movableView.find( '.movable-name' ).text( 'Group X' );
        movableView.find( '.action-move' ).on( 'click',
            function()
            {
                if( selectedMovable )
                {
                    selectedMovable = null;
                    $( this ).removeClass( 'action-toggled' );
                    world.events.hex_field_click.pop( moveTo );
                }
                else
                {
                    selectedMovable = movable;
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

        return movableView;
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
                /* Show or hide the sector view, depending on whether the clicked hex contains movables
                 */
                const movables = world.getMovables( x, y );
                if( movables )
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
