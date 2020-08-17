;
// Through js enhance user experience. Do not need to send to backend to make a judgement every time
var user_register_ops=  {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".login_wrap .do-register").click( function(){
            var btn_target = $(this)
            if(btn_target.hasClass('disabled')){
                common_ops.alert("Processing..")
                return;
            }
            btn_target.addClass("disabled");
            btn_target.removeClass('disabled');
            window.location.href = common_ops.buildUrl("/user/register");
        });
    }
};

$(document).ready( function(){
    user_register_ops.init();
});
