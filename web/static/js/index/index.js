var index_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        window.onload = function(){
            $.ajax({
                url:common_ops.buildUrl( "/" ),
                type:'POST',
                data:'',
                dataType:'json',
                success:function( res ){
                    if( res.code == 200 ){
                        $('#ul_gold_cross').html(res.html_gold_cross);
                        $('#ul_nh').html(res.html_nh);
                        $('#ul_second_up').html(res.html_second_up);
                        selector_ops.init();
                    }
                }
            });
        };
    }
};

$(document).ready( function(){
    index_ops.init();
} );