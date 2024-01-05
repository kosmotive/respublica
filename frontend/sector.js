function sector( api, world, build )
{
    const events =
    {
    };

    /* Creates a new celestial view.
     */
    function createCelestialView( sector, celestial )
    {
        celestial.name = world.getCelestialName( sector, celestial );

        const celestialView = $( '#celestial-template' ).clone();
        celestialView.appendTo( '#sector-view' );
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
        celestialView.find( '.celestial-star' ).attr( 'src', `img/celestial-star-${ celestial.features.variant }.svg` );
        switch( celestial.features.variant )
        {

        case 'white-mainline': 
            variant = 'White / Mainline';
            break;

        case 'yellow-mainline': 
            variant = 'Yellow / Mainline';
            break;

        case 'blue-mainline': 
            variant = 'Blue / Mainline';
            break;

        case 'white-dwarf':
            variant = 'White Dwarf';
            break;

        case 'red-giant':
            variant = 'Red Giant';
            break;

        }
        if( variant ) features += `<li>${ variant }</li>`;
        for( const [key, value] of Object.entries( celestial.features ) )
        {
            if( key != 'type' && key != 'variant' )
            {
                var formattedValue;
                switch( key )
                {

                case 'capacity':
                    formattedValue = celestial.habitated_by ? `${ celestial.remaining_capacity }/${ value }` : value;
                    break;

                default:
                    formattedValue = value;

                };
                featureName = key.charAt( 0 ).toUpperCase() + key.slice( 1 );
                features += `<li>${ featureName }: ${ formattedValue }</li>`
            }
        }
        celestialView.find( '.celestial-features' ).html( features );
        if( !celestial.habitated_by )
        {
            celestialView.find( '.celestial-habitated' ).remove();
        }

        /* Determine whether there is a celestial habitated by the player within the current sector.
         */
        const sectorHabitated = sector.celestial_set.some( ( c ) => { return c.habitated_by == world.game.empire.url; } );

        /* Setup actions.
         */
        if( celestial.habitated_by === null && sectorHabitated ) // the celestial is unhabitated but the player already has another celestial habitated in the same sector
        {
            celestialView.find( '.celestial-actions-develop' ).on( 'click',
                function()
                {
                    build.develop( sector, celestial );
                }
            );
            celestialView.find( '.celestial-actions-build' ).remove();
        }
        else
        if( celestial.habitated_by != world.game.empire.url ) // the celestial is habitated by a different player
        {
            celestialView.find( '.celestial-actions-develop' ).remove();
            celestialView.find( '.celestial-actions-build' ).remove();
        }
        else // the celestial is habitated by the player
        {
            celestialView.find( '.celestial-actions-develop' ).remove();
            celestialView.find( '.celestial-actions-build' ).on( 'click',
                function()
                {
                    build.openMenu( sector, celestial );
                }
            );
        }
        return celestialView;
    }

    /* Load all constructions (by celestial).
     */
    var constructions = {};
    const loadConstructions = $.get( api.url + '/constructions',
        function( data )
        {
            for( const construction of data )
            {
                if( !Object.keys( constructions ).includes( construction.celestial ) )
                {
                    constructions[ construction.celestial ] = []
                }
                constructions[ construction.celestial ].push( construction );
            }
        }
    );

    /* Load the content.
     */
    $.when( loadConstructions ).done(
        function()
        {
            $( document ).ready(
                function()
                {
                    if( $( '#sector-view' ).length )
                    {
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
                                        celestial.constructions = Object.keys( constructions ).includes( celestial.url ) ? constructions[ celestial.url ] : [];
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
                }
            );
        }
    );

    const ret =
    {
        events: events
    };
    return ret;
}
