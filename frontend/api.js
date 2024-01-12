function api( url )
{
    function getCookie( name )
    {
        var cookieValue = null;
        if( document.cookie && document.cookie != '' )
        {
            var cookies = document.cookie.split( ';' );
            for( var i = 0; i < cookies.length; i++ )
            {
                var cookie = jQuery.trim( cookies[ i ] );
                if( cookie.substring( 0, name.length + 1 ) == ( name + '=' ) )
                {
                    cookieValue = decodeURIComponent( cookie.substring( name.length + 1 ) );
                    break;
                }
            }
        }
        return cookieValue;
    }

    const config = {
        redirect403: true,
        csrfToken: getCookie( 'csrftoken' )
    };

    $( document ).ajaxError( function( event, jqXHR, settings, thrownError )
    {
        switch( jqXHR.status )
        {
            case 403:
                if( config.redirect403 && !settings.ignore403 )
                {
                    if( !location.href.endsWith( '/login.html' ) )
                    {
                        location.href = 'login.html';
                    }
                    break;
                }
    
            default:
                console.log('Error ' + jqHXR.status);
    
        }
    });

    function augmentRequestWithCSRFToken( xhr, settings )
    {
        xhr.setRequestHeader( 'X-CSRFToken', config.csrfToken );
    }

    return {
        url: url,
        config: config,
        augmentRequestWithCSRFToken: augmentRequestWithCSRFToken
    };
}
