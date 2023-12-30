function api( url )
{
    $( document ).ajaxError( function( event, jqXHR, settings, thrownError )
    {
        switch( jqXHR.status )
        {
            case 403:
                location.href = 'login.html';
                break;
    
            default:
                console.log('Error ' + jqHXR.status);
    
        }
    });

    return {
        url: url
    };
}
