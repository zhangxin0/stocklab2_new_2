;
// 将表单发送至后端
var set_sale_point_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $("#set_sale_point").click( function(){
           var sale_point_target = $('#set_sale_point_div input[name=set_sale_point]');
           var sale_point = sale_point_target.val();
           var data = {
                'sale_point': sale_point,
           };
           if(sale_point.length < 1){
                //alert( "请输入卖点!");
                common_ops.tip("请输入卖点！",sale_point_target);
                return false;
           }
           $.ajax({
                url: common_ops.buildUrl( "/user_defined_set_sale_point" ),
                async:false,
                type:'POST',
                data:data,
                dataType:'json',
                success:function( resp ){
                    if(resp.code == 200){
                        common_ops.alert("卖点设置成功！");
                        set_sale_point_ops.init();
                    }
                    if(resp.code == -1){
                        common_ops.alert("卖点格式错误，请输入符合规范的卖点！");
                    }
                 }
            });
        });
      }
};



$(document).ready(function(){
    set_sale_point_ops.init();
});