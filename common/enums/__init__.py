# coding:utf-8
"""
枚举工具类
"""


def _to_str(concrete_enum, value):
    """
    labels转换
    """
    if not value:
        return unicode('')

    if hasattr(concrete_enum, '__labels__'):
        return concrete_enum.__labels__.get(int(value))
    return unicode(value)


def labels(cls):
    """
    枚举描述定义
    """
    cls.label = classmethod(_to_str)
    return cls
