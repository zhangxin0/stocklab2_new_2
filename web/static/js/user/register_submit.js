;
// Through js enhance user experience. Do not need to send to backend to make a judgement every time
var user_register_submit_ops=  {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".login_wrap .do-submit").click( function(){
            var btn_target = $(this)
            if(btn_target.hasClass('disabled')){
                common_ops.alert("正在处理，请稍后.")
                return;
            }

            var login_name_target = $(".login_wrap input[name=login_name]");
            var login_name = login_name_target.val();
            var login_pwd_target = $(".login_wrap input[name=login_pwd]");
            var login_pwd = login_pwd_target.val();
            var login_pwd2_target = $(".login_wrap input[name=login_pwd2]");
            var login_pwd2 = login_pwd2_target.val();
            var mobile_target = $(".login_wrap input[name=mobile]");
            var mobile = mobile_target.val();
            var email_target = $(".login_wrap input[name=email]");
            var email = email_target.val();
            var nick_name_target = $(".login_wrap input[name=nick_name]");
            var nick_name = nick_name_target.val();


            if(login_name == undefined || login_name.length<1){
                common_ops.tip("请输入用户名!",login_name_target);
                return;
            }
            if(nick_name == undefined || nick_name.length<1){
                common_ops.tip("请输入昵称!",nick_name_target);
                return;
            }
            if(login_pwd == undefined || login_pwd.length<1){
                common_ops.tip("请输入密码!",login_pwd_target);
                return;
            }
            if(login_pwd2 == undefined || login_pwd2.length<1){
                common_ops.tip("请输入确认密码!",login_pwd2_target);
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

            if (login_pwd!=login_pwd2){
                common_ops.tip( "确认密码有误!",login_pwd2_target);
                $("input[name=login_pwd2]").val('');
                $("input[name=login_pwd2]").append('<style>.confirmation::placeholder{color:red; opacity:0.4;}</style>');
                return false
            }

            $.ajax({
                url:common_ops.buildUrl("/user/register_submit"),
                type:'POST',
                data:{ 'login_name':login_name,'login_pwd':login_pwd,'mobile':mobile,'email':email,'nick_name':nick_name },
                dataType:'json',
                // res get from backend
                success:function(res){
                // leave out side if
                     btn_target.removeClass('disabled');
                     if(res.code == 200){
                        common_ops.alert("注册成功!");
                        window.location.href = common_ops.buildUrl("/");
                     }
                     if(res.code == -1){
                        common_ops.tip("用户名已存在，请重新输入!",login_name_target);
                        $(".login_wrap input[name=login_name]").val('');
                        $(".login_wrap input[name=login_name]").append('<style>.login_name::placeholder{color:red; opacity:0.4;}</style>');
                     }
                     // no matter login right or wrong response with the alert
                }
            });
        });
    }
};

$(document).ready( function(){
    user_register_submit_ops.init();
});