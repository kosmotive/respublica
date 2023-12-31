function movables( api, world )
{
    const events =
    {
    };

    /* Creates a new movable view.
     */
    function createMovableView( movable )
    {
        const movableView = $( '#movable-template' ).clone();
        movableView.appendTo( '#movables-list' );
        movableView.attr( 'id', '' );

        const shipTemplate = movableView.find( '#ship-template' ).clone();
        for( const ship in movable.ship_set )
        {
            const shipView = shipTemplate.clone();
            shipView.attr( 'id', '' );
            shipView.appendTo( movableView.find( '.ship-list' ) );
            shipView.text( ship );
        }
        shipTemplate.remove();

        console.log( movable );
        return movableView;
    }

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
