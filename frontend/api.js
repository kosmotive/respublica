function api( url )
{
    const config = {
        redirect403: true
    };

    $( document ).ajaxError( function( event, jqXHR, settings, thrownError )
    {
        switch( jqXHR.status )
        {
            case 403:
                if( config.redirect403 )
                {
                    location.href = 'login.html';
                    break;
                }
    
            default:
                console.log('Error ' + jqHXR.status);
    
        }
    });

    return {
        url: url,
        config: config
    };
}
