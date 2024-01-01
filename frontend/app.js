/* Load CallbackStack.
 */
$.ajax({
    url: 'callbacks.js',
    dataType: 'script',
    async: false
});


/* Load modules.
 */
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


/* Plug the modules together.
 */
const app = Object()

app.api        = loadModule( 'api'       , url = 'http://127.0.0.1:8000/api' );
app.blueprints = loadModule( 'blueprints', api = app.api );
app.world      = loadModule( 'world'     , api = app.api, blueprints = app.blueprints, hexFieldSize = 200 );
app.login      = loadModule( 'login'     , api = app.api );
app.build      = loadModule( 'build'     , api = app.api, world = app.world, blueprints = app.blueprints );
app.sector     = loadModule( 'sector'    , api = app.api, world = app.world, build = app.build );
app.movables   = loadModule( 'movables'  , api = app.api, world = app.world );
