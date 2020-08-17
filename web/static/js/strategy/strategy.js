;

function clock(){
   $.ajax({
        url: common_ops.buildUrl( "/get_strategy" ),
        type:'GET',
        success:function( resp ){
            if (resp.code==200){
                $('#strategy_paragraph').html(resp.data);
                var symbols = resp.symbol;
                var operations = resp.operation;
                symbols = symbols.substr(0, symbols.length - 1);
                operations = operations.substr(0, operations.length - 1);
                symbols = symbols.split(',');
                operations=operations.split(',');
                for(i=0;i<symbols.length;i++){
                    var msg={
                        'phone': resp.phone,
                        'symbol':  symbols[i],
                        'operation': operations[i],
                    };
                    $.ajax({
                        url: common_ops.buildUrl( "/message" ),
                        type:'POST',
                        data: msg,
                        success:function(){

                        }
                    });
                }
            }
        }
    });
}

setInterval(clock,5000);//动态更新时间