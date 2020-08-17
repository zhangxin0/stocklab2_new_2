;
var upColor = '#ec0000';
var upBorderColor = '#8A0000';
var downColor = '#00da3c';
var downBorderColor = '#008F28';
// 数据意义：开盘(open)，收盘(close)，最低(lowest)，最高(highest)
var read_name = $(".api").attr('name');
var read_symbol = $(".api").attr('symbol');
var read_data = $(".api").attr('id');
read_data = read_data.replace(/'/g, '"');
var data = JSON.parse(read_data);
var data0 = splitData(data);
// 获取目标价，买入价和当前价 显示在图上
var buy_price = $(".api").attr('buy_price');

function splitData(rawData) {
    var categoryData = [];
    var values = [];
    var volumns = [];
    for (var i = 0; i < rawData.length; i++) {
        // splice(index,operation,content) eg: months.splice[1,0,'Feb'] insert Feb at position 1 / operation:1 replace
        // ["2018-01-09", 35.63, 35.84, 34.95, 36.11, vol] (0,1) remove element at position 0 and return [35.63, 35.84, 34.95, 36.11]
        categoryData.push(rawData[i].splice(0, 1)[0]);
        values.push(rawData[i]);
        volumns.push(rawData[i][4]);
    }
    return {
        categoryData: categoryData,
        values: values,
        volumns:volumns
    };
}

function calculateMA(dayCount,data0) {
    var result = [];
    for (var i = 0, len = data0.values.length; i < len; i++) {
        if (i < dayCount) {
            result.push('-');
            continue;
        }
        var sum = 0;
        for (var j = 0; j < dayCount; j++) {
            sum += data0.values[i - j][1];
        }
        result.push((sum / dayCount).toFixed(2));
    }
    return result;
}


function genPrice(buy_price,data0) {
    var result = [];
    for (var i = 0, len = data0.values.length; i < len; i++) {
        result.push(buy_price);
    }
    return result;
}

function setOption(data0,read_name,read_symbol){
    option = {
        legend: {
            data: ['日K', 'MA5', 'MA10', 'MA20', 'MA30','MA60','MA144','MA233','MA377','MA610','买入','卖出'],
        },
        title: {
            text: read_name+' '+read_symbol,
            left: 0
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
        },//link K figure and volumns figure
        axisPointer: {
            link: {xAxisIndex: 'all'},
            label: {
                backgroundColor: '#777'
            }
        },
        toolbox: {
            right:'3.28%',
            feature: {
                dataZoom: {
                    yAxisIndex: false
                },
                brush: {
                    type: ['lineX', 'clear']
                }
            }
        },
        brush: {
            xAxisIndex: 'all',
            brushLink: 'all',
            outOfBrush: {
                colorAlpha: 0.1
            }
        },
        grid: [
            // K data
            {
                left: '2.5%',
                right: '4%',
                height: '70%'
            },// Vol
            {
                left: '2.5%',
                right: '4%',
                bottom: '5%',
                height: '8%',
            }
        ],
        xAxis: [
            {
                type: 'category',
                data: data0.categoryData,
                scale: true,
                boundaryGap: false,
                axisLine: {onZero: false},
                splitLine: {show: false},
                splitNumber: 20,
                min: 'dataMin',
                max: 'dataMax'
            },
            {
                type: 'category',
                gridIndex: 1,
                data: data0.categoryData,
                scale: true,
                boundaryGap : false,
                axisLine: {onZero: false},
                axisTick: {show: false},
                splitLine: {show: false},
                axisLabel: {show: false},
                splitNumber: 20,
                min: 'dataMin',
                max: 'dataMax',
                axisPointer: {
                    label: {
                        formatter: function (params) {
                            var seriesValue = (params.seriesData[0] || {}).value;
                            return params.value
                            + (seriesValue != null
                                ? '\n' + echarts.format.addCommas(seriesValue)
                                : ''
                            );
                        }
                    }
                }
            }
        ],
        yAxis: [
            {
                scale: true,
                splitArea: {
                    show: false,
                }
            },
            {
                scale: true,
                gridIndex: 1,
                splitNumber: 2,
                axisLabel: {show: false},
                axisLine: {show: false},
                axisTick: {show: false},
                splitLine: {show: false}
            }
        ],
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: [0, 1],
                start: 90,
                end: 100
            },
            {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                left: '1.6%',
                right: '3.64%',
                bottom: '0%',
                height:'4%',
                start: 90,
                end: 100
            }
        ],
        series: [
            {
                name: '日K',
                type: 'candlestick',
                data: data0.values,
                itemStyle: {
                    color: upColor,
                    color0: downColor,
                    borderColor: upBorderColor,
                    borderColor0: downBorderColor
                },
            // delete markpoint and markline
            },
            {
                name: 'MA5',
                type: 'line',
                data: calculateMA(5,data0),
                smooth: true,
                lineStyle: {
                    opacity: 1,
                    color:'red',
                }
            },
            {
                name: 'MA10',
                type: 'line',
                data: calculateMA(10,data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.8,
                    color:'#bea419',
                }
            },
            {
                name: 'MA20',
                type: 'line',
                data: calculateMA(20,data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.6,
                    color:'#92159e',
                }
            },
            {
                name: 'MA30',
                type: 'line',
                data: calculateMA(30,data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.4
                }
            },
            {
                name: 'MA60',
                type: 'line',
                data: calculateMA(60,data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.4,
                    color:'#19a3d7',
                }
            },
            {
                name: 'MA144',
                type: 'line',
                data: calculateMA(144,data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.4
                }
            },
            {
                name: 'MA233',
                type: 'line',
                data: calculateMA(233,data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.4
                }
            },
            {
                name: 'MA377',
                type: 'line',
                data: calculateMA(377,data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.4
                }
            },
            {
                name: 'MA610',
                type: 'line',
                data: calculateMA(610,data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.4
                }
            },
            {
                name: '买入',
                type: 'line',
                data: genPrice(buy_price, data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.4,
                    type:'dashed',
                    color:'blue',
                }
            },
            {
                name: '卖出',
                type: 'line',
                data: genPrice((buy_price*1.05).toFixed(2), data0),
                smooth: true,
                lineStyle: {
                    opacity: 0.4,
                    color: 'red',
                    type:'dashed',
                }
            },
            {
                name: '成交量',
                type: 'bar',
                data: data0.volumns,
                xAxisIndex: 1,
                yAxisIndex: 1
            }
        ]
    };
    return option;
}

var myChart = echarts.init(document.getElementById('main'));
myChart.hideLoading();
option = setOption(data0,read_name,read_symbol);
myChart.setOption(option,true);
window.onresize = myChart.resize;

//添加refreshChart函数,点击search后重新绘图:
var search_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".search_wrapper .search").click( function(){
           var search_target = $('.search_wrapper input[name=stockname]');
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
                        buy_price = resp.buy_price
                        var myChart = echarts.init(document.getElementById('main'));
                        myChart.hideLoading();
                        option = setOption(data0,resp['name'],resp['symbol']);
                        myChart.setOption(option,true);
                        // 这里只更新了图，没有对价格栏进行更新:
                        var html = '';
                        if(buy_price){
                            buy_price = buy_price.toFixed(2);
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
        });
    }
};



$(document).ready(function(){
    search_ops.init();
});