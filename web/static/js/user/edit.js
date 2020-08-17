;
var user_edit_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".edit_wrap .do-modify").click( function(){
            var btn_target = $(this);
            if (btn_target.hasClass("disabled")){
                common.ops.alert("正在处理，请稍后.")
                return;
            }
            var login_name_target = $(".edit_wrap input[name=login_name]");
            var login_name = $(".edit_wrap input[name=login_name]").val();
            var mobile_target = $(".edit_wrap input[name=mobile]");
            var mobile = $(".edit_wrap input[name=mobile]").val();
            var email_target = $(".edit_wrap input[name=email]");
            var email = $(".edit_wrap input[name=email]").val();
            var nickname_target = $(".edit_wrap input[name=nickname]");
            var nickname = $(".edit_wrap input[name=nickname]").val();

            if(login_name == undefined || login_name.length<1){
                common_ops.tip("请输入用户名!",login_name_target);
                return;
            }
            if(nickname == undefined || nickname.length<1){
                common_ops.tip("请输入昵称!",nickname_target);
                return;
            }
            if(mobile == undefined || mobile.length<1){
                common_ops.tip("请输入手机号码!",mobile_target);
                return;
            }
            if(email == undefined || email.length<1){
                common_ops.tip("请输入邮箱!",email_target);
                return;
            }

            btn_target.addClass("disabled");
            $.ajax({
                url:common_ops.buildUrl("/user/edit"),
                type:'POST',
                data:{ 'login_name':login_name,'mobile':mobile,'email':email,'nickname':nickname},
                dataType:'json',
                // res get from backend
                success:function(res){
                // leave out side if
                     btn_target.removeClass('disabled');
                     if(res.code == 200){
                        common_ops.alert("修改完成!");
                        window.location.href = common_ops.buildUrl("/");
                     }
                     if(res.code == -1){
                        common_ops.alert("用户名已存在，请重新输入!");
                        $(".edit_wrap input[name=user_name]").val('');
                        $(".edit_wrap input[name=user_name]").append('<style>.user_name::placeholder{color:red; opacity:0.4;}</style>');
                     }
                     // no matter login right or wrong response with the alert
                }
            });
        });
    }
};

$(document).ready(function(){
    user_edit_ops.init();
});