function movables( api, world )
{
    const events =
    {
    };

    /* Creates a new movable view.
     */
    function createMovableView( sector, movable )
    {
        const movableView = $( '#movable-template' ).clone();
        movableView.prependTo( '#movables-view' );
        movableView.attr( 'id', '' );
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
                $( '#movables-view' ).fadeIn( 200 );
            });
        }
    })

    const ret =
    {
        events: events
    };
    return ret;
}
