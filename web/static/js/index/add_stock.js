;
// 将表单发送至后端
var submit_form = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $("#add_stock_button").click( function(){
           var symbol_target = $('#form_div input[name=add_symbol]');
           var date_target = $('#form_div input[name=add_date]');
           var price_target = $('#form_div input[name=add_price]');
           var symbol = symbol_target.val();
           var date = date_target.val();
           var price = price_target.val();
           var data = {
                'symbol': symbol,
                'date':date,
                'price':price,
           };
           if(symbol.length < 6){
                //alert( "请输入符合规范的股票代码");
                common_ops.tip("请输入符合规范的股票代码！",symbol_target);
                return false;
           }
           if(date.length != 8){
                //alert( "请输入符合规范的日期，例如：20200101");
                common_ops.tip("请输入符合规范的日期，例如：20200101.",date_target);
                return false;
           }
           if(price.length < 1){
                //alert( "请输入符合规范的股票代码");
                common_ops.tip("请输入买入价格！",price_target);
                return false;
           }
           $.ajax({
                url: common_ops.buildUrl( "/user_defined_add_list" ),
                async:false,
                type:'POST',
                data:data,
                dataType:'json',
                success:function( resp ){
                    if(resp.code == 200){
                        $("#stock_list").html(resp.data);
                        selector_ops.init();
                    }
                    if(resp.code == -1){
                        common_ops.alert("股票代码错误，请输入正确的股票代码！");
                    }
                 }
            });
        });
      }
};



$(document).ready(function(){
    submit_form.init();
});