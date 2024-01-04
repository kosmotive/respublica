$.fn.popup = function()
{
    if( !this.hasClass( 'popup' ) ) return;
    const content = this;

    const curtain = $( '<div id="popup-curtain"></div>' );
    curtain.appendTo( $( 'body' ) );
    curtain.on( 'click',
        function()
        {
            $( '#popup-curtain' ).remove();
            content.fadeOut( 200 );
        }
    );

    content.fadeIn( 200 );
}

