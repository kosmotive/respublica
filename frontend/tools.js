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


/* Convert HSL color representation to hex code.
 *
 * Based upon: https://stackoverflow.com/a/44134328
 */
function hsl2hex( h, s, l )
{
    const a = s * Math.min( l, 1 - l );
    const f = n => {
      const k = ( n + h * 360 / 30 ) % 12;
      const color = l - a * Math.max( Math.min( k - 3, 9 - k, 1 ), -1 );
      return Math.round( 255 * color ).toString( 16 ).padStart( 2, '0' );
    };
    return `#${ f( 0 ) }${ f( 8 ) }${ f( 4 ) }`;
}
