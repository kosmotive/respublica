function sector( api, world, build )
{
    const events =
    {
    };

    /* Creates a new celestial view.
     */
    function createCelestialView( sector, celestial )
    {
        celestial.name = sector.name + ( celestial.position > 0 ? ' ' + celestial.position : '' );

        const celestialView = $( '#celestial-template' ).clone();
        celestialView.prependTo( '#sector-view' );
        celestialView.attr( 'id', '' );
        celestialView.find( '.celestial-name' ).text( celestial.name );
        for( const type of [ 'star', 'planet' ] )
        {
            if( celestial.features.type != type )
            {
                celestialView.find( '.celestial-' + type ).remove();
            }
        }
        var features = '', variant = undefined;
        celestialView.find( '.celestial-star' ).hide();
        switch( celestial.features.variant )
        {

        case 'white-mainline': 
            celestialView.find( '.celestial-star-mainline .star-brush' ).attr( 'fill', 'silver' );
            celestialView.find( '.celestial-star-mainline' ).show();
            variant = 'White / Mainline';
            break;

        case 'yellow-mainline': 
            celestialView.find( '.celestial-star-mainline .star-brush' ).attr( 'fill', 'orange' );
            celestialView.find( '.celestial-star-mainline' ).show();
            variant = 'Yellow / Mainline';
            break;

        case 'blue-mainline': 
            celestialView.find( '.celestial-star-mainline .star-brush' ).attr( 'fill', 'dodgerblue' );
            celestialView.find( '.celestial-star-mainline' ).show();
            variant = 'Blue / Mainline';
            break;

        case 'white-dwarf':
            celestialView.find( '.celestial-star-white-dwarf' ).show();
            variant = 'White Dwarf';
            break;

        case 'red-giant':
            celestialView.find( '.celestial-star-red-giant' ).show();
            variant = 'Red Giant';
            break;

        }
        if( variant ) features += `<li>${ variant }</li>`;
        for( const [key, value] of Object.entries( celestial.features ) )
        {
            if( key != 'type' && key != 'variant' )
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
        if( celestial.habitated_by != world.game.empire.url )
        {
            celestialView.find( '.celestial-options' ).remove();
        }
        else
        {
            celestialView.find( '.celestial-options' ).on( 'click',
                function()
                {
                    build.openMenu( sector, celestial );
                }
            );
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
