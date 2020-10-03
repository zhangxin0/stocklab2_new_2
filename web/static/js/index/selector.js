;
/* 本文件功能：
* 3个选股算法的 点击事件
* ajax返回参数改写element html后，监听失效，如何重启"点击"监听？
*
* */
//只刷新指定div:选股结果 load只能执行一次

var selector_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $("#nh_selector").click(function(){
            var btn_target = $(this);
            $("#nh_selector").html("选股中，请稍等..");
            // if (btn_target.hasClass("disabled")){
            //         common_ops.alert("正在选股...请稍后");
            //         return;
            //  }
            btn_target.addClass("disabled");
            $.ajax({
                url:common_ops.buildUrl( "/nh_predict" ),
                type:'GET',
                success:function( res ){
                    if(res.code == 200){
                        $("#nh_selector").html("粘合选股");
                        common_ops.alert("更新完成！");
                        // 刷新选股结果: 刷新选股结果div
                        $("#ul_nh").innerHTML(res.html);
                        btn_target.removeClass('disabled');
                        // selector_ops.init();
                    }
                    if(res.code == -1){
                        $("#nh_selector").html("粘合选股");
                        // 刷新选股结果: 刷新选股结果div
                        common_ops.alert("选股结果已更新！");
                        $("#ul_nh").innerHTML(res.html);
                        btn_target.removeClass('disabled');
                        // selector_ops.init();
                    }
                }
            });
        });

        $("#gold_cross_selector").click(function(){
            var btn_target = $(this);
            $("#gold_cross_selector").html("选股中，请稍等..");
            // if (btn_target.hasClass("disabled")){
            //         common_ops.alert("正在选股...请稍后");
            //         return;
            //  }
            btn_target.addClass("disabled");
            $.ajax({
                url:common_ops.buildUrl( "/gold_cross_predict" ),
                type:'GET',
                success:function( res ){
                    if(res.code == 200){
                        $("#gold_cross_selector").html("金叉选股");
                        // 刷新选股结果: 刷新选股结果div
                        common_ops.alert("更新完成！");
                        $("#ul_gold_cross").innerHTML(res.html);
                        btn_target.removeClass('disabled');
                        // selector_ops.init();
                        // 点击完毕后，stock list监听点击取消

                    }
                    if(res.code == -1){
                        $("#gold_cross_selector").html("金叉选股");
                        // 刷新选股结果: 刷新选股结果div
                        common_ops.alert("选股结果已更新！");
                        $("#ul_gold_cross").innerHTML(res.html);
                        btn_target.removeClass('disabled');
                        // selector_ops.init();
                    }
                }
            });
        });

        $("#second_up_selector").click(function(){
            var btn_target = $(this);
            $("#second_up_selector").html("选股中，请稍等..");
            // if (btn_target.hasClass("disabled")){
            //         common_ops.alert("正在选股...请稍后");
            //         return;
            //  }
            btn_target.addClass("disabled");
            $.ajax({
                url:common_ops.buildUrl( "/second_up_predict" ),
                type:'GET',
                success:function( res ){
                    if(res.code == 200){
                        $("#second_up_selector").html("二次反弹");
                        // 刷新选股结果: 刷新选股结果div
                        common_ops.alert("更新完成！");
                        $("#ul_second_up").innerHTML(res.html);
                        btn_target.removeClass('disabled');
                        // selector_ops.init();
                    }
                    if(res.code == -1){
                        $("#second_up_selector").html("二次反弹");
                        // 刷新选股结果: 刷新选股结果div
                        common_ops.alert("选股结果已更新！");
                        $("#ul_second_up").innerHTML(res.html);
                        btn_target.removeClass('disabled');
                        // selector_ops.init();
                    }
                }
            });
        });
        // 点击移除持股列表:
        $("#stockList").ready(function(){
            // 持股列表检测点击： !如果没有选股结果， undefined error
            var obj_lis = $("#stock_list li span");
            var obj_trash = $("#stock_list li span i");
            for(i=0;i<obj_lis.length;i++){
                // 检测是否删除 ajax 本身是异步请求，请求时，i已经等于3
                obj_trash[i].onclick = function(){
                   symbol = $(this).parent().html().slice(52,61);
                   var callback = {
                        'ok':function(){
                            $.ajax({
                                url: common_ops.buildUrl( "/delete_list" ),
                                async:false,
                                type:'POST',
                                data:{'symbol':symbol},
                                dataType:'json',
                                success:function( resp ){
                                    $("#stock_list").html(resp.data);
                                    // selector_ops.init();
                                    // window.location.href = common_ops.buildUrl( "/" );
                                 }
                            });
                        },
                        'cancel':null
                   };
                   common_ops.confirm("确定要将"+symbol+"从持股列表中移除吗？",callback);
                }
                obj_lis[i].onclick = function(){
                    // 获取5-13位
                    var symbol = $(this).html().slice(52,61);
                    var data = {
                        'symbol': symbol,
                   };
                   $.ajax({
                        url: common_ops.buildUrl( "/search" ),
                        async:false,
                        type:'POST',
                        data:data,
                        dataType:'json',
                        success:function( resp ){
                            if(resp.code == 200){
                                //window.location.href = common_ops.buildUrl( "/" );
                                // 数据意义：开盘(open)，收盘(close)，最低(lowest)，最高(highest)
                                  // 同一页面下js之间可以互相调用,这里调用plot_figure下的js
                                  var read_data = resp.data0;
                                  var data0 = splitData(read_data);
                                  // 更新buy_price
                                  buy_price = resp.buy_price
                                  var myChart = echarts.init(document.getElementById('main'));
                                  myChart.hideLoading();
                                  option = setOption(data0,resp['name'],resp['symbol']);
                                  myChart.setOption(option,true);
                                  // 这里只更新了图，没有对价格栏进行更新:
                                  var html = '';
                                  if(buy_price){
                                      goal_price = (buy_price*1.04).toFixed(2);
                                      html=  "<h2 id='current_price'>当前价:----</h2>" + "<h2 id='goal_price'> &nbsp;&nbsp;&nbsp;&nbsp;买入价:"+buy_price+"&nbsp;&nbsp;&nbsp;&nbsp;目标价:"+goal_price+"</h2>";
                                  }else{
                                       html=  "<h2 id='current_price'>当前价:----</h2>";
                                  }
                                  $("#price_holder").html(html);
                            }
                            if(resp.code == -1){
                                common_ops.alert("股票代码错误，请输入正确的股票代码！");
                            }
                         }
                    });
                }
            }
            // 选股结果列表检测点击:
            var obj_lis1 = $(".selectorList li span");
            var obj_add = $(".selectorList li i");
            for(i=0;i<obj_lis1.length;i++){
                // 检测是否删除 ajax 本身是异步请求，请求时，i已经等于3
                obj_add[i].onclick = function(){
                      symbol = $(this).parent().html().slice(46,55);
                      var callback = {
                           'ok':function(){
                               $.ajax({
                                  url:common_ops.buildUrl('/add_list'),
                                  type:'POST',
                                  async:false,
                                  data:{'symbol':symbol},
                                  success:function(resp){
                                      // 刷新stock_list div
                                      if(resp['code']==200){
                                         $("#stock_list").html(resp.data);
                                      }
                                      // selector_ops.init();
                                      //window.location.href = common_ops.buildUrl( "/" );
                                  }
                              });
                           },
                           'cancel':null
                      };
                      common_ops.confirm("选股结果为:"+symbol+",是否第二天以开盘价购买？",callback);
                }
                // 检测span单击(add单击同时，也执行了span单击），除非停止事件迁移。
                obj_lis1[i].onclick = function(){
                    // 获取5-13位
                    var symbol = $(this).html().slice(46,55);
                    var data = {
                        'symbol': symbol,
                   };
                   $.ajax({
                        url: common_ops.buildUrl( "/search" ),
                        async:false,
                        type:'POST',
                        data:data,
                        dataType:'json',
                        success:function( resp ){
                            if(resp.code == 200){
                                //window.location.href = common_ops.buildUrl( "/" );
                                // 数据意义：开盘(open)，收盘(close)，最低(lowest)，最高(highest)
                                // 同一页面下js之间可以互相调用,这里调用plot_figure下的js
                                var read_data = resp.data0;
                                var data0 = splitData(read_data);
                                // 更新buy_price
                                buy_price = resp.buy_price
                                var myChart = echarts.init(document.getElementById('main'));
                                myChart.hideLoading();
                                option = setOption(data0,resp['name'],resp['symbol']);
                                myChart.setOption(option,true);
                                // 这里只更新了图，没有对价格栏进行更新:
                                var html = '';
                                if(buy_price){
                                    goal_price = (buy_price*1.05).toFixed(2);
                                    html=  "<h2 id='current_price'>当前价:----</h2>" + "<h2 id='goal_price'> &nbsp;&nbsp;&nbsp;&nbsp;买入价:"+buy_price+"&nbsp;&nbsp;&nbsp;&nbsp;目标价:"+goal_price+"</h2>";
                                }else{
                                     html=  "<h2 id='current_price'>当前价:----</h2>";
                                }
                                $("#price_holder").html(html);
                            }
                            if(resp.code == -1){
                                common_ops.alert("股票代码错误，请输入正确的股票代码！");
                            }
                         }
                    });
                }
            }
        });
    }
};

$(document).ready( function(){
    selector_ops.init();
} );