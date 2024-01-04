function build( api, world, blueprints )
{
    const events =
    {
    };

    /* Load the content.
     */
    $( document ).ready( function()
    {
        $( '#buildscreen' ).hide();
        $( '#buildscreen .close-button' ).on( 'click',
            function()
            {
                $( '#buildscreen' ).fadeOut( 200 );
            }
        );
    })

    function setBuildProcess( process, sector, celestial )
    {
        if( process )
        {
            var name;
            if( process.data.blueprint_url )
            {
                const blueprint = blueprints.get( process.data.blueprint_url );
                name = blueprint.data.name;
            }
            else
            {
                var target;
                for( celestial2 of sector.celestial_set )
                {
                    if( celestial2.url == process.data.celestial_url )
                    {
                        target = world.getCelestialName( sector, celestial2 );
                    }
                }
                name = `Developing ${ target } for exploitation`;
            }
            const view = $( '#buildscreen .build-process-info' )

            var turns = process.end_tick - world.game.tick;
            turns = turns == 1 ? `${ turns } turn` : `${ turns } turns`;

            const progress = `${ Math.round( 100 * ( world.game.tick - process.start_tick ) / ( process.end_tick - process.start_tick ) ) }%`

            view.find( '.build-process-name' ).text( name );
            view.find( '.build-process-celestial' ).text( world.getCelestialName( sector, celestial ) );
            view.find( '.build-process-progress' ).text( progress );
            view.find( '.build-process-remaining' ).text( turns );

            $( '#buildscreen .build-process-none' ).hide();
            $( '#buildscreen .build-process-info' ).show();
        }
        else
        {
            $( '#buildscreen .build-process-none' ).show();
            $( '#buildscreen .build-process-info' ).hide();
        }
    }

    function build( sector, celestial, blueprint )
    {
        $.ajax({
            type: 'POST',
            url: blueprint.url + 'build/',
            contentType: 'application/json',
            data: `{"celestial":"${ celestial.url }"}`,
            beforeSend: api.augmentRequestWithCSRFToken,
            success: function( process )
            {
                sector.process = process;
                setBuildProcess( process, sector, celestial );
            }
        });
    }

    function develop( sector, celestial )
    {
        function _openMenu()
        {
            openMenu( sector, celestial );
            $( '#buildscreen' ).addClass( 'hide-options' );
            $( '#buildscreen' ).addClass( 'hide-constructions' );
        }
        function _develop()
        {
            $.ajax({
                type: 'POST',
                url: celestial.url + 'colonialize/',
                contentType: 'application/json',
                beforeSend: api.augmentRequestWithCSRFToken,
                success: function( process )
                {
                    sector.process = process;
                    _openMenu();
                }
            });
        }
        if( sector.process )
        {
            $.get( sector.process,
                function( process )
                {
                    console.log(process);
                    if( process.handler_id != 'ColonializationHandler' || process.data.celestial_url != celestial.url )
                    {
                        _develop();
                    }
                    else
                    {
                        _openMenu();
                    }
                }
            );
        }
        else
        {
            _develop();
        }
    }

    function openMenu( sector, celestial )
    {
        $( '#buildscreen .sector-name' ).text( sector.name );
        $( '#buildscreen .celestial-name' ).text( celestial.name );
        $( '#buildscreen .build-process-info' ).hide();
        $( '#buildscreen' ).removeClass( 'hide-options' );
        $( '#buildscreen' ).removeClass( 'hide-constructions' );

        for( const blueprintUrl of world.game.empire.blueprint_set )
        {
            blueprints.require( blueprintUrl );
        }
        blueprints.resolve();
        blueprints.whenResolved(
            function()
            {
                /* Fetch info on current build process in this sector.
                 */
                setBuildProcess( null );
                if( sector.process )
                {
                    $.get( sector.process,
                        function( process )
                        {
                            $.get( process.data.celestial_url,
                                function( processCelestial )
                                {
                                    setBuildProcess( process, sector, processCelestial );
                                }
                            );
                        }
                    );
                }

                /* Create constructions list.
                 */
                const constructions = [];
                if( celestial.constructions.length )
                {
                    $( '#buildscreen .constructions-list li:not(#construction-template)' ).remove();
                    for( const construction of celestial.constructions )
                    {
                        const blueprint = blueprints.get( construction.blueprint );
                        constructions.push( blueprint.base_id );

                        const constructionView = $( '#construction-template' ).clone();
                        constructionView.attr( 'id', '' );
                        constructionView.attr( 'url', blueprint.url );
                        constructionView.find( '.construction-name' ).text( blueprint.data.name );
                        constructionView.find( '.construction-size' ).text( blueprint.data.size );
                        constructionView.appendTo( $( '#buildscreen .constructions-list' ) );
                    }
                }

                /* Create build options.
                 */
                if( world.game.empire.blueprint_set.length )
                {
                    $( '#buildscreen .build-options-list li:not(#build-option-template)' ).remove();
                    for( const blueprintUrl of world.game.empire.blueprint_set )
                    {
                        const blueprint = blueprints.get( blueprintUrl );
                        const requirements = blueprint.requirements.map( blueprints.resolveBaseIdToName ).join( ', ' );
                        const requirementsOk = blueprint.requirements.every( ( requirement ) => constructions.includes( requirement ) );

                        const buildOption = $( '#build-option-template' ).clone();
                        buildOption.attr( 'id', '' );
                        buildOption.attr( 'url', blueprint.url );
                        buildOption.find( '.build-option-name' ).text( blueprint.data.name );
                        buildOption.find( '.build-option-cost' ).text( blueprint.data.cost );
                        if( !requirementsOk )
                        {
                            buildOption.addClass( 'requirements-not-satisfied' );
                        }
                        if( blueprint.data.size )
                        {
                            buildOption.find( '.build-option-size' ).text( blueprint.data.size );
                        }
                        else
                        {
                            buildOption.find( '.build-option-size' ).remove();
                        }
                        if( requirements.length )
                        {
                            buildOption.find( '.build-option-requirements' ).text( requirements );
                        }
                        else
                        {
                            buildOption.find( '.build-option-requirements' ).remove();
                        }
                        buildOption.appendTo( $( '#buildscreen .build-options-list' ) );

                        if( requirementsOk )
                        {
                            buildOption.on( 'click',
                                function()
                                {
                                    build( sector, celestial, blueprint );
                                }
                            );
                        }
                    }
                }

                /* Show the build screen.
                 */
                $( '#buildscreen' ).fadeIn( 200 );
            }
        );
    }

    const ret =
    {
        events: events,
        openMenu: openMenu,
        develop: develop
    };
    return ret;
}
