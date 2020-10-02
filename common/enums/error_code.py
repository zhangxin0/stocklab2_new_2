# coding: utf-8
from enum import Enum

from common.enums import labels


@labels
class ErrorCode(Enum):
    """
    错误代码定义
    """
    SUCCESS = 0
    DIRTY_DATA = 1
    UNAUTHORIZED = 2
    LOGIN_REQUIRED = 3
    VALIDATION_FAILED = 4
    INVALID_PARAM_ERROR = 5
    INVALID_STATUS_ERROR = 6
    ERROR = 100
    CRM_ERROR = 500
    STA_ERROR = 501

    __labels__ = {
        SUCCESS: u"访问成功",
        DIRTY_DATA: u"脏数据",
        UNAUTHORIZED: u"权限问题",
        LOGIN_REQUIRED: u"登录问题",
        VALIDATION_FAILED: u"校验错误",
        INVALID_PARAM_ERROR: u"参数错误",
        INVALID_STATUS_ERROR: u"非法状态",
        ERROR: u"未知问题",
    }


