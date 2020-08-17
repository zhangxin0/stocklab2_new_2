# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, make_response, redirect, g
from common.libs.Helper import ops_render
from common.models.User import User
from common.libs.user.UserService import UserService
import json
from application import app, db
from common.libs.UrlManager import UrlManager

route_user = Blueprint('user_page', __name__)

@route_user.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return ops_render("user/login.html")
    resp = {'code': 200, 'msg': '登陆成功！', 'data': {}}
    req = request.values
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''
    # 参数有效性校验
    if login_name is None or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = "用户名格式错误！"
        return jsonify(resp)

    if login_pwd is None or len(login_pwd) < 1:
        resp['code'] = -1
        resp['msg'] = "密码格式错误！"
        return jsonify(resp)

    user_info = User.query.filter_by(login_name=login_name).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = '用户名不存在！'
        return jsonify(resp)

    if user_info.login_pwd != UserService.genePwd(login_pwd, user_info.login_salt):
        resp['code'] = -1
        resp['msg'] = '密码错误！'
        return jsonify(resp)
    response = make_response(json.dumps(resp))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], '%s#%s' % (UserService.geneAuthCode(user_info), user_info.uid))
    return response

@route_user.route("/register", methods=["GET"])
def register():
    return ops_render("user/register.html")


@route_user.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "GET":
        return ops_render("user/edit.html")
    resp = {'code': 200, 'msg': 'Login Success!', 'data': {}}
    req = request.values
    # 判断用户是否存在：
    res = User.query.filter_by(login_name=req['login_name']).first()
    user = User.query.filter_by(uid=g.current_user.uid).first()
    if res and res.login_name != g.current_user.login_name:
        resp['code'] = -1
    else:
        # sqlachemy
        user.login_name = req['login_name']
        user.email = req['email']
        user.nickname = req['nickname']
        user.mobile = req['mobile']
        try:
            db.session.commit()
        except Exception as e:
            app.logger.info(e)
    response = make_response(resp)
    # 修改完用户信息后，重置cookie，不然会自动退出：
    if resp['code'] == 200:
        g.current_user = User.query.filter_by(login_name=user.login_name).first()
        response.set_cookie(app.config['AUTH_COOKIE_NAME'],"%s#%s"%(UserService.geneAuthCode(g.current_user),g.current_user.uid))
    return response


@route_user.route("/register_submit", methods=["POST"])
def register_submit():
    resp = {'code': 200, 'msg': 'Login Success!', 'data': {}}
    req = request.values
    user = User()
    # 判断用户明是否存在：
    res = User.query.filter_by(login_name=req['login_name']).first()
    if res:
        resp['code'] = -1
    else:
        # sqlachemy
        user.login_name = req['login_name']
        user.login_salt = UserService.geneSalt(16)
        user.login_pwd = UserService.genePwd(req['login_pwd'],user.login_salt)
        user.email = req['email']
        user.nickname = req['nick_name']
        user.mobile = req['mobile']
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            app.logger.info(e)
    response = make_response(resp)
    # 更新cookie为新用户cookie，完成新用户登陆，防止旧用户cookie登陆
    if resp['code'] == 200:
        g.current_user = User.query.filter_by(login_name=user.login_name).first()
        response.set_cookie(app.config['AUTH_COOKIE_NAME'],"%s#%s"%(UserService.geneAuthCode(g.current_user),g.current_user.uid))
    return response

@route_user.route("/reset-pwd", methods=["GET", "POST"])
def resetPwd():
    if request.method == "GET":
        return ops_render("user/reset_pwd.html")
    resp = {'code': 200, 'msg': '修改成功！', 'data': {}}
    req = request.values
    old_password = req['old_password'] if 'old_password' in req else ''
    new_password = req['new_password'] if 'new_password' in req else ''
    user_info = g.current_user
    if UserService.genePwd(old_password,user_info.login_salt) != user_info.login_pwd:
        resp['code'] = -1
        resp['msg'] = '旧密码错误!'
        return jsonify(resp) # dict json序列化为对象
    user_info.login_pwd = UserService.genePwd(new_password,user_info.login_salt)
    db.session.commit()

    # update cookie:
    response = make_response(json.dumps(resp))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], '%s#%s' % (UserService.geneAuthCode(user_info), user_info.uid),
                        60 * 60 * 24 * 120)  # save for 120 days
    return response


@route_user.route('/logout')
def logout():
    response = make_response(redirect(UrlManager.buildUrl('/user/login')))
    response.delete_cookie(app.config['AUTH_COOKIE_NAME'])
    return response


