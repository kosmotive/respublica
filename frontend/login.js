function login( api )
{
    $( document ).ready( function()
    {
        if( $( '#login' ).length )
        {
            $( '#login' ).on( 'submit', function( event )
            {
                event.preventDefault();

                $.ajax({
                    type: 'POST',
                    url: api + $( '#login' ).attr('action'),
                    data: $( '#login' ).serialize(),
                    statusCode:
                    {
                        400: function( data )
                        {
                            console.log( data.responseJSON );
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