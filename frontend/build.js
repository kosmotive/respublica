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

    function setBuildProcess( process )
    {
        if( process )
        {
            const blueprint = blueprints.get( process.data.blueprint_url );
            const view = $( '#buildscreen .build-process-info' )

            var turns = process.end_tick - world.game.tick;
            turns = turns == 1 ? `${ turns } turn` : `${ turns } turns`;

            const progress = `${ Math.round( 100 * ( world.game.tick - process.start_tick ) / ( process.end_tick - process.start_tick ) ) }%`

            view.find( '.build-process-name' ).text( blueprint.data.name );
            view.find( '.build-process-celestial' ).text( process.data.celestial_url );
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
                setBuildProcess( process );
            }
        });
    }

    function openMenu( sector, celestial )
    {
        $( '#buildscreen .sector-name' ).text( sector.name );
        $( '#buildscreen .celestial-name' ).text( celestial.name );
        $( '#buildscreen .build-process-info' ).hide();

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
                if( sector.process )
                {
                    $.get( sector.process, setBuildProcess );
                }
                else
                {
                    setBuildProcess( null );
                }

                /* Create build options.
                 */
                $( '#buildscreen .build-options-list' ).empty();
                for( const blueprintUrl of world.game.empire.blueprint_set )
                {
                    const blueprint = blueprints.get( blueprintUrl );
                    const buildOption = $( `<li class="build-option" url="${ blueprint.url }">${ blueprint.data.name }</li>` );
                    buildOption.appendTo( $( '#buildscreen .build-options-list' ) );
                    buildOption.on( 'click',
                        function()
                        {
                            build( sector, celestial, blueprint );
                        }
                    );
                }
                $( '#buildscreen' ).fadeIn( 200 );
            }
        );
    }

    const ret =
    {
        events: events,
        openMenu: openMenu
    };
    return ret;
}
