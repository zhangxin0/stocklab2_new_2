;

function clock(){
   $.ajax({
        url: common_ops.buildUrl( "/get_price" ),
        type:'GET',
        success:function( resp ){
            if (resp.code==200){
                $('#current_price').html("当前价:"+resp.data);
            }
        }
    });
}

setInterval(clock,1000);//动态更新时间





