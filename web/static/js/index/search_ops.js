//添加refreshChart函数,点击search后重新绘图:
;
var search_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".search_wrapper #search_stock").click(function(){
           var search_target = $('#form_container input[name=stockname]');
           var symbol = search_target.val();
           var data = {
                'symbol': symbol,
           };
           if(symbol.length < 6){
                //alert( "请输入符合规范的股票代码");
                common_ops.tip("请输入符合规范的股票代码！",search_target);
                return false;
           }
           $.ajax({
                url: common_ops.buildUrl( "/search" ),
                async:false,
                type:'POST',
                data:data,
                dataType:'json',
                success:function( resp ){
                    if(resp.code == 200){
                        // 数据意义：开盘(open)，收盘(close)，最低(lowest)，最高(highest)
                        var read_data = resp.data0;
                        var data0 = splitData(read_data);
                        // 更新buy_price
                        buy_price = resp.buy_price;
                        sale_point = parseFloat(resp.sale_point);
                        var myChart = echarts.init(document.getElementById('main'));
                        myChart.hideLoading();
                        option = setOption(data0,resp['name'],resp['symbol']);
                        myChart.setOption(option,true);
                        // 这里只更新了图，没有对价格栏进行更新:
                        var html = '';
                        if(buy_price){
                            buy_price = buy_price.toFixed(2);
                            goal_price = (buy_price*(100+sale_point)/100).toFixed(2);
                            html= "<h2 id='current_price'>当前价:----</h2>" + "<h2 id='goal_price'> &nbsp;&nbsp;&nbsp;&nbsp;买入价:"+buy_price+"&nbsp;&nbsp;&nbsp;&nbsp;目标价:"+goal_price+"&nbsp;&nbsp;&nbsp;&nbsp;当前卖点:"+sale_point+"%</h2>" + "<h2 id='current_rps'>&nbsp;&nbsp;&nbsp;&nbsp;RPS:更新中(每90 s)...</h2>";
                        }else{
                            html= "<h2 id='current_price'>当前价:----</h2>"+"<h2 id='sale_point'>&nbsp;&nbsp;&nbsp;&nbsp; 当前卖点:"+sale_point+"%</h2>" + "<h2 id='current_rps'>&nbsp;&nbsp;&nbsp;&nbsp;RPS:更新中(每90 s)...</h2>";
                        }
                        $("#price_holder").html(html);
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
    search_ops.init();
});