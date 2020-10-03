//添加refreshChart函数,点击search后重新绘图:
;
var get_history = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $("#page_1").click(function(){
           var history_target = $('#history_tbody');
           var page_target = $(this);
           var page = page_target.text();
           var data = {
               "page":page,
           };
           $.ajax({
                url: common_ops.buildUrl( "/get_history" ),
                async:false,
                type:'GET',
                data:data,
                dataType:'json',
                success:function( resp ){
                    history_target.html(resp.data['html_history_list']);
                }
           });
        });

        $("#page_2").click(function(){
           var history_target = $('#history_tbody');
           var page_target = $(this);
           var page = page_target.text();
           var data = {
               "page":page,
           };
           $.ajax({
                url: common_ops.buildUrl( "/get_history" ),
                async:false,
                type:'GET',
                data:data,
                dataType:'json',
                success:function( resp ){
                    history_target.html(resp.data['html_history_list']);
                }
           });
        });
        $("#page_3").click(function(){
           var history_target = $('#history_tbody');
           var page_target = $(this);
           var page = page_target.text();
           var data = {
               "page":page,
           };
           $.ajax({
                url: common_ops.buildUrl( "/get_history" ),
                async:false,
                type:'GET',
                data:data,
                dataType:'json',
                success:function( resp ){
                    history_target.html(resp.data['html_history_list']);
                }
           });
        });
        $("#previous").click(function(){
           var history_target = $('#history_tbody');
           var previous_target = $('#previous');
           var data = {
               "previous":true,
           };
           $.ajax({
                url: common_ops.buildUrl( "/get_history" ),
                async:false,
                type:'GET',
                data:data,
                dataType:'json',
                success:function( resp ){
                    if(!resp.data['disable'] && Number($("#page_1").text())>1){
                        $("#page_1").text(Number($("#page_1").text())-1);
                        $("#page_2").text(Number($("#page_2").text())-1);
                        $("#page_3").text(Number($("#page_3").text())-1);
                    }
                    if(resp.data['page'] >=0){
                         history_target.html(resp.data['html_history_list']);
                    }
                }
           });
        });
        $("#next").click(function(){
           var history_target = $('#history_tbody');
           var next_target = $('#next');
           var data = {
               "next":true,
           };
           $.ajax({
                url: common_ops.buildUrl( "/get_history" ),
                async:false,
                type:'GET',
                data:data,
                dataType:'json',
                success:function( resp ){
                    if(!resp.data['disable'] && Number($("#page_3").text()) < resp.data['max_page']){
                        $("#page_1").text(Number($("#page_1").text())+1);
                        $("#page_2").text(Number($("#page_2").text())+1);
                        $("#page_3").text(Number($("#page_3").text())+1);
                    }
                    history_target.html(resp.data['html_history_list']);
                }
           });
        });
    }
};



$(document).ready(function(){
    get_history.init();
});