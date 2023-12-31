function sector( api, world )
{
    const events =
    {
    };

    /* Creates a new celestial view.
     */
    function createCelestialView( sector, celestial )
    {
        const celestialView = $( '#celestial-template' ).clone();
        celestialView.prependTo( '#sector-view' );
        celestialView.attr( 'id', '' );
        celestialView.find( '.celestial-name' ).text( sector.name + ( celestial.position > 0 ? ' ' + celestial.position : '' ) );
        for( const type of [ 'star', 'planet' ] )
        {
            if( celestial.features.type != type )
            {
                celestialView.find( '.celestial-' + type ).remove();
            }
        }
        var features = ''
        for( const [key, value] of Object.entries( celestial.features ) )
        {
            if( key != 'type' )
            {
                featureName = key.charAt( 0 ).toUpperCase() + key.slice( 1 );
                features += `<li>${ featureName }: ${ value }</li>`
            }
        }
        celestialView.find( '.celestial-features' ).html( features );
        if( !celestial.habitated_by )
        {
            celestialView.find( '.celestial-habitated' ).remove();
        }
        return celestialView;
    }

    /* Load the content.
     */
    $( document ).ready( function()
    {
        if( $( '#sector-view' ).length )
        {
            $( '#sector-view' ).hide();
            world.events.hex_field_click.push( function( x, y, sectorUrl )
            {
                /* Show or hide the sector view, depending on whether the clicked hex field is a sector
                 */
                if( sectorUrl )
                {
                    $.get( sectorUrl + '?depth=1', function( sector )
                    {
                        $( '#sector-view .sector-name' ).text( sector.name );
                        $( '#sector-view .celestial:not(#celestial-template)' ).remove();

                        /* Load celestials.
                         */
                        for( const celestial of sector.celestial_set )
                        {
                            createCelestialView( sector, celestial );
                        }

                        $( '#sector-view' ).fadeIn( 200 );
                    });
                }
                else
                {
                    $( '#sector-view' ).fadeOut( 200 );
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
