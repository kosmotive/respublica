function blueprints( api )
{
    /* Maps blueprint URLs to the the actual blueprint data.
     */
    const blueprintsData = {};

    /* Maps blueprint `base_id` field to the name of the blueprint.
     */
    const blueprintNames = {}

    function require( blueprintUrl )
    {
        if( !( blueprintUrl in Object.keys(blueprintsData ) ) )
        {
            blueprintsData[ blueprintUrl ] = null;
        }
    }

    function get( blueprintUrl )
    {
        return blueprintsData[ blueprintUrl ];
    }

    const ajaxCalls = [];
    function resolve()
    {
        for( const blueprintUrl of Object.keys( blueprintsData ) )
        {
            var blueprint = blueprintsData[ blueprintUrl ];
            if( blueprint === null )
            {
                const ajaxCall = $.get( blueprintUrl, function( blueprint )
                {
                    blueprintsData[ blueprintUrl ] = blueprint;
                    if( !Object.keys( blueprintNames ).includes( blueprint.base_id ) )
                    {
                        blueprintNames[ blueprint.base_id ] = blueprint.data.name;
                    }
                });
                ajaxCalls.push( ajaxCall );
            }
        }
    }

    function isResolved()
    {
        for( const blueprint of Object.values( blueprintsData ) )
        {
            if( blueprint === null ) return false;
        }
        return true;
    }

    function whenResolved( then )
    {
        if( isResolved() )
        {
            then();
        }
        else
        {
            $.when( ...ajaxCalls ).done( function()
            {
                then();
            });
        }
    }

    const ret =
    {
        require: require,
        resolve: resolve,
        whenResolved: whenResolved,
        get: get,
        resolveBaseIdToName: function( baseId ) { return blueprintNames[ baseId ]; }
    };
    return ret;
}
