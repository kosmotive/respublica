$.fn.popup = function()
{
    if( !this.hasClass( 'popup' ) ) return;
    const popup  = this;
    const parent = popup.parent();

    const curtain = $( '<div id="popup-curtain"></div>' );
    curtain.appendTo( $( 'body' ) );
    curtain.on( 'click',
        function()
        {
            popup.fadeOut( 200,
                function()
                {
                    popup.appendTo( parent );
                    popup.css( 'left', '' );
                    popup.css(  'top', '' );
                    $( '#popup-curtain' ).remove();
                }
            );
        }
    );

    popup.fadeIn( 200 );

    const offset = popup.offset();
    popup.appendTo( curtain );
    popup.css( 'left', offset.left - curtain.offset().left );
    popup.css(  'top', offset.top  - curtain.offset().top  );
}

