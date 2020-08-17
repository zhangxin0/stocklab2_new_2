;
var mod_pwd_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".do-modify").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("正在处理，请稍后.");
                return;
            }
            var old_password_target = $("input[name=old_password]");
            var old_password = $("input[name=old_password]").val();
            var new_password_target = $("input[name=new_password]");
            var new_password = $("input[name=new_password]").val();
            var new_password2_target = $("input[name=new_password2]");
            var new_password2 = $("input[name=new_password2]").val();

            if( !old_password ){
                common_ops.tip( "请输入旧密码!",old_password_target );
                return false;
            }
            if( !new_password || new_password.length < 1 ){
                common_ops.tip( "请输入新密码!",new_password_target );
                return false;
            }
            if (new_password!=new_password2){
                common_ops.tip( "确认密码有误!",new_password2_target );
                $("input[name=new_password2]").val('');
                $("input[name=new_password2]").append('<style>.confirmation::placeholder{color:red; opacity:0.4;}</style>');
                return false
            }

            if (old_password == new_password){
                common_ops.tip("新密码和旧密码相同!", new_password_target)
                $("input[name=new_password]").val('');
                $("input[name=new_password]").append('<style>.new_password::placeholder{color:red; opacity:0.4;}</style>');
                $("input[name=new_password2]").val('');
                $("input[name=new_password2]").append('<style>.confirmation::placeholder{color:red; opacity:0.4;}</style>');
                return false;
            }


            btn_target.addClass("disabled");

            var data = {
                old_password: old_password,
                new_password: new_password
            };

            $.ajax({
                url:common_ops.buildUrl( "/user/reset-pwd" ),
                type:'POST',
                data:data,
                dataType:'json',
                success:function( res ){
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href = common_ops.buildUrl("/");
                        }
                    }
                    common_ops.alert( res.msg,callback );
                }
            });


        });
    }
};

$(document).ready( function(){
    mod_pwd_ops.init();
} );