function CallbackStack()
{
    this.list = [];
}

CallbackStack.prototype = {

    push: function( fn )
    {
        this.list.push( fn );
    },

    pop: function()
    {
        this.list.pop();
    },

    fire: function(...args)
    {
        for( var idx = this.list.length - 1; idx >= 0; --idx )
        {
            if( !this.list[ idx ]( ...args ) ) break;
        }
    }

};
