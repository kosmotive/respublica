function movables( api, world )
{
    var selectedMovable = null;
    const events =
    {
    };

    /* Creates a new movable view.
     */
    function createMovableView( movable )
    {
        const movableView = $( '#movable-template' ).clone();
        movableView.appendTo( $( '#movables-view .movables-list' ) );
        movableView.attr( 'id', '' );
        movableView.find( '.movable-name' ).text( 'Group X' );
        movableView.find( '.action-move' ).on( 'click',
            function()
            {
                if( selectedMovable )
                {
                    selectedMovable = null;
                    $( this ).removeClass( 'action-toggled' );
                }
                else
                {
                    selectedMovable = movable;
                    $( this ).addClass( 'action-toggled' );
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

    /* Dispatch "move_to" actions when the map is clicked and a movable is selected.
     */
    world.events.hex_field_click.add(
        function( x, y, sectorUrl )
        {
            if( !selectedMovable ) return;
            $.post({
                url: selectedMovable.url + 'move_to/',
                contentType: 'application/json',
                data: `{"x":${x}, "y":${y}}`
            });
            selectedMovable = null;
        }
    );

    /* Load the content.
     */
    $( document ).ready( function()
    {
        if( $( '#movables-view' ).length )
        {
            $( '#movables-view' ).hide();
            world.events.hex_field_click.add( function( x, y, sectorUrl )
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
            });
        }
    })

    const ret =
    {
        events: events
    };
    return ret;
}
