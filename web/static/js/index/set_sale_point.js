;
// 将表单发送至后端
var set_sale_point_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $("#set_sale_point").click( function(){
           var symbol_target = $('#set_sale_point_div input[name=set_symbol]');
           var cut_point_target = $('#set_sale_point_div input[name=set_cut_point]');
           var profit_point_target = $('#set_sale_point_div input[name=set_profit_point]');
           var buy_price_target = $('#set_sale_point_div input[name=set_buy_price]');
           var symbol = symbol_target.val();
           var cut_point = cut_point_target.val();
           var profit_point = profit_point_target.val();
           var buy_price = buy_price_target.val();
           var data = {
                'symbol': symbol,
                'cut_point': cut_point,
                'profit_point': profit_point,
                'buy_price': buy_price
           };
           if(symbol.length < 1){
                //alert( "请输入卖点!");
                common_ops.tip("请输入股票代码！",symbol_target);
                return false;
           }
           if(buy_price.length < 1){
                //alert( "请输入卖点!");
                common_ops.tip("请输入买入价格！",buy_price_target);
                return false;
           }
           $.ajax({
                url: common_ops.buildUrl( "/add_notify" ),
                async:false,
                type:'POST',
                data:data,
                dataType:'json',
                success:function( resp ){
                    if(resp.code == 200){
                        common_ops.alert("卖点设置成功！");
                        set_sale_point_ops.init();
                        window.location.replace("/");
                    }
                    if(resp.code == -1){
                        common_ops.alert("股票代码输入错误，请输入符合规范的代码！");
                    }
                 }
            });
        });
      }
};



$(document).ready(function(){
    set_sale_point_ops.init();
});