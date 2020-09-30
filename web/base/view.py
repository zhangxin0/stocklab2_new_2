# coding:utf-8
import functools
import time
import traceback
from functools import partial

from credit.common.exception import APIException
from sqlalchemy.exc import OperationalError
from flask import request

from credit.common.error_code import ErrorCode
from credit.common.exceptions.exception import *
from credit.common.i18nstr import ExceptionStr
from credit.common.response_util import ResponseUtil
from credit.common.utils.log import Log
from credit.view.web.hook.flask_hook import global_data


def restful(func=None, form_class=None):
    """
    Restful API 装饰器
    """
    # Decorator without parameter
    if func is None:
        return partial(restful, form_class=form_class)

    if not callable(func):
        raise TypeError('func must be callable')

    def _get_form_data(request_):
        """
        获取 WTForms 校验的实体
        """
        if request_.method == 'GET':
            form_data = request_.args
        elif request_.method in ['PUT', 'POST', 'DELETE']:
            form_data = request_.get_json()
        else:
            raise ViewException(ErrorCode.INVALID_PARAM_ERROR.value, u"只支持 GET/PUT/POST/DELETE")
        return form_data

    @functools.wraps(func)
    def _func(*args, **kwargs):
        """
        1. validate form;
        2. catch exception;
        """
        logger = Log.get_logger()

        try:
            # 用 Form 解析 request
            if form_class is not None:
                form_data = _get_form_data(request)

                form = form_class.from_json(form_data, meta={'locales': [request.lang, 'zh']})
                form.verify()

                result = func(form, *args, **kwargs)
            else:
                result = func(*args, **kwargs)

        except APIException as ex:
            from credit.repository.dao import db
            db.session.rollback()

            logger.warn(u"FATAL: status_code=[%s] exception=[%s]", ex.error_code, ex.message)
            result = ResponseUtil.error_response(msg=ex.message)

        except CreditException as ex:
            from credit.repository.dao import db
            db.session.rollback()

            logger.warn(u"FATAL: status_code=[%s] exception=[%s]", ex.code, ex.message)
            result = ResponseUtil.error_response(msg=ex.msg)

        except OperationalError as ex:
            # 对于底层数据库连接引起的错误, 避免使用rollback()
            from credit.repository.dao import db
            error_id = long(time.time())
            logger.exception(u"FATAL OperationalError: %s %s" % (error_id, ex))
            session = db.session.registry()
            session.invalidate()
            return ResponseUtil.error_response(msg=ExceptionStr.SYSTEM_ERROR.format(error_id=error_id))

        except Exception as ex:
            from credit.repository.dao import db
            db.session.rollback()
            error_id = int(time.time())

            traceback.print_exc()
            logger.exception(u"FATAL OperationalError: %s %s" % (error_id, ex))
            result = ResponseUtil.error_response(msg=ExceptionStr.SYSTEM_ERROR.format(error_id=error_id))

        return result

    return _func


def convert_form_2_dto(form, req_dto):
    """
    :param form:
    :param req_dto:
    :return:
    """
    dto = req_dto()
    form.populate_obj(dto)
    dto.authorizer_id = global_data.authorizer_id   # 授权人
    dto.employee_id = global_data.employee_id       # 登陆人

    return dto

