function login( api )
{
    $( document ).ready( function()
    {
        if( $( '#login' ).length )
        {
            api.config.redirect403 = false;

            $( '#login' ).on( 'submit', function( event )
            {
                event.preventDefault();

                $.ajax({
                    type: 'POST',
                    url: api.url + $( '#login' ).attr('action'),
                    data: $( '#login' ).serialize(),
                    statusCode:
                    {
                        400: function( data )
                        {
                            for( const [key, value] of Object.entries( data.responseJSON ) )
                            {
                                $( '#login-' + key + ' p' ).text( value );
                            }
                        }
                    },
                    success: function( data )
                    {
                        $( '#login p.error' ).text( '' );
                        location.href = 'index.html';
                    }
                });
            });
        }
    });

    return {
    };
}
