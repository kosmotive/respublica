function loadModule( module, ...args )
{
    this.load = 
    $.ajax({
        url: `${ module }.js`,
        dataType: 'script',
        async: false
    });
    return eval( `${ module }( ...args )` );
}


const app = Object()

app.api   = loadModule( 'api'  , url = 'http://127.0.0.1:8000/api' );
app.world = loadModule( 'world', api = app.api, hexFieldSize = 200 );
app.login = loadModule( 'login', api = app.api );
