;

function clock_rps(){
   $.ajax({
        url: common_ops.buildUrl( "/get_rps" ),
        type:'GET',
        success:function( resp ){
            if (resp.code==200){
                $('#current_rps').html(resp.html);
            }
        }
    });
}

setInterval(clock_rps,6*60000);//动态更新时间





