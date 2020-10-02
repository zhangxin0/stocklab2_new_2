# coding: utf-8
"""
exception definitions
"""
from common.enums.error_code import ErrorCode


class StocklabException(Exception):
    """
    异常基础类
    """

    def __init__(self, code_0=None, msg=""):
        """
        授信异常实例化
        :param code_0: 100 by default
        :param msg: empty by default
        """
        super(StocklabException, self).__init__(msg)

        self.code = code_0 or ErrorCode.ERROR.value
        self.msg = msg or ErrorCode.label(self.code)


class InvalidStatusException(StocklabException):
    """
    非法状态异常
    """

    def __init__(self, msg=''):
        """
        非法状态异常默认参数
        """
        code = ErrorCode.INVALID_STATUS_ERROR.value
        msg = msg or ErrorCode.label(code)
        super(InvalidStatusException, self).__init__(code, msg)


class InvalidParamException(StocklabException):
    """
    参数校验异常
    """

    def __init__(self, msg=''):
        """
        参数校验异常默认参数
        """
        code = ErrorCode.INVALID_PARAM_ERROR.value
        msg = msg or ErrorCode.label(code)
        super(InvalidParamException, self).__init__(code, msg)


class AccessDeniedException(StocklabException):
    """
    权限校验异常
    """

    def __init__(self, msg=''):
        """
        权限校验异常默认参数
        """
        code = ErrorCode.UNAUTHORIZED.value
        msg = msg or ErrorCode.label(code)
        super(AccessDeniedException, self).__init__(code, msg)


class DaoException(StocklabException):
    """
    Dao层统一异常类
    """

    def __init__(self, error_code, msg=u''):
        """
        Dao层统一异常类初始化
        """
        super(DaoException, self).__init__(error_code, msg)


class ServiceException(StocklabException):
    """
    Service层统一异常类
    """

    def __init__(self, error_code, msg=u''):
        """
        Service层统一异常类初始化
        """
        super(ServiceException, self).__init__(error_code, msg)


class ViewException(StocklabException):
    """
    View层统一异常类
    """

    def __init__(self, error_code, msg=u''):
        """
        View层统一异常类
        """
        super(ViewException, self).__init__(error_code, msg)


class RetryException(Exception):
    """
    当定时任务抛出这种exception时，说明任务需要在一定时间间隔后重试，不需要要进行报错
    """
    pass
