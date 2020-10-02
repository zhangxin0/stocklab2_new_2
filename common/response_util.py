# -*- coding: utf-8 -*-
import json
import decimal
from flask import Response, jsonify, request
from datetime import datetime, date

from web.base.stocklab_request import SUCCESS_CODE, FAILURE_CODE
from common.utils.date_util import DateUtil


class ObjEncoder(json.JSONEncoder):

    def default(self, obj):
        from common.utils.num_util import NumberUtil

        if isinstance(obj, decimal.Decimal):
            return str(NumberUtil.retain_decimal(obj))
        elif isinstance(obj, datetime):
            return DateUtil.format_time_str(obj)
        elif isinstance(obj, date):
            return DateUtil.format_date(obj)
        elif isinstance(obj, int):
            return str(obj)
        return obj.__dict__


class ResponseUtil(object):
    """
    Response 工具类
    """

    @classmethod
    def success_response(cls, data=None, msg=u""):
        """
        :param data:
        :param msg:
        :return:
        """
        result = _SuccessResponse(data, msg=msg)
        return Response(json.dumps(result, cls=ObjEncoder, sort_keys=True, indent=4),
                        mimetype='application/json')

    @classmethod
    def error_response(cls, data=None, code=FAILURE_CODE, msg=u""):
        """
        :param data:
        :param code:
        :param msg:
        :return:
        """
        result = _ErrorResponse(data, code, msg)
        return Response(json.dumps(result, cls=ObjEncoder, sort_keys=True, indent=4),
                        mimetype='application/json')

    @classmethod
    def response(cls, data=None, code=SUCCESS_CODE, msg=u"success"):
        """
        :param data:
        :param code:
        :param msg:
        :return:
        """
        result = _ApiResponse(data, code=code, msg=msg)
        return Response(json.dumps(result, cls=ObjEncoder, sort_keys=True, indent=4),
                        mimetype='application/json')

    @classmethod
    def api_response(cls, success=True, data=None, message=""):
        """
        api接口返回response
        :param success:
        :param data:
        :param message:
        :return:
        """
        return jsonify({
            "success": success,
            "data": data,
            "message": message
        })

    @classmethod
    def list_response(cls, data=None, code=SUCCESS_CODE, msg=None, total=None, **kwargs):
        result = _ListResponse(data=data, code=code, msg=msg, total=total, **kwargs)
        return Response(json.dumps(result, cls=ObjEncoder, sort_keys=True, indent=4),
                        mimetype='application/json')


class _ApiResponse(object):
    """

    """

    def __init__(self, data, code=SUCCESS_CODE, msg=u""):
        """

        :param data:
        :param code:
        :param msg:
        """
        self.data = data
        self.code = code
        self.msg = msg


class _ErrorResponse(_ApiResponse):
    """

    """

    def __init__(self, data, code=FAILURE_CODE, msg=u'内部发生错误'):
        """

        :param data:
        :param msg:
        """
        super(_ErrorResponse, self).__init__(data, code, msg=msg)


class _SuccessResponse(_ApiResponse):
    """

    """

    def __init__(self, data, msg=u"成功"):
        """

        :param data:
        :param msg:
        """
        super(_SuccessResponse, self).__init__(data, code=SUCCESS_CODE, msg=msg)


class _ListResponse(_ApiResponse):
    def __init__(self, data, code=SUCCESS_CODE, msg=None, total=None, **kwargs):
        super(_ListResponse, self).__init__(data=data, code=code)
        self.data = {
            "list": data
        }
        if total is not None:
            self.data.update({
                "total": total
            })
        if kwargs:
            self.data.update(kwargs)
        if msg:
            self.msg = msg
