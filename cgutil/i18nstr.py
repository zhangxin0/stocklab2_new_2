# coding: utf-8
# 多语言基础字符串类


class I18NStr(object):
    """
    一个需要进行多语言翻译转化的字符串
    """
    def __init__(self, key, default_val, **kwargs):
        """
        :param key:             该字符串在starling平台对应的key
        :param default_val:     当没有找到对应翻译时，使用的默认字符串
        :param kwargs:          对于获取的翻译value和default_val中支持{}的插值参数，类似"客户ID[id={customer_id}]不存在"
                                该字典用于进行后续的插值，字典中的value，可以同样是一个I18NStr
        """
        self.key = key
        self.default_val = default_val
        self.format_items = kwargs

    def format(self, **kwargs):
        """
        格式化函数，用于对于获取的翻译value或default_val进行插值
        """
        assert 'key' not in kwargs
        assert 'default_val' not in kwargs

        format_items = dict(self.format_items)
        format_items.update(kwargs)

        # 每次format返回新的I18NStr
        return I18NStr(self.key, self.default_val, **format_items)

    def encode(self, *args, **kwargs):
        """
        当rpc接口的resp中包含I18NStr时，底层框架会调用encode函数，以此对于数据进行处理
        rpc本身是没有语言设定的，默认是采用default_val进行处理
        :return:
        """
        return str(self).encode(*args, **kwargs)

    def __str__(self):
        res = self.default_val or self.key
        if res and self.format_items:
            res = res.format(**self.format_items)
        return res


class I18NListJoinStr(object):
    """
    国际化拼接字符串, 用于多个I18NStr拼接的场景, 一般在接口返回时统一处理
    """
    def __init__(self, i18n_str_list, joiner=','):
        """
        :param i18n_str_list:   list<I18NStr>
        :param joiner:          字符串format时使用的分隔符
        """
        self.str_list = i18n_str_list
        self.joiner = joiner


class I18NCustomStr(object):
    """
    自定义实现的国际化字符串
    """
    def __init__(self, get_val_func):
        """
        get_val_func(lang), 返回具体翻译字符串的自定义函数
        """
        self.get_val_func = get_val_func


class I18NDepartmentNameStr(object):
    """
    部门名称的字符串类型，用于对于部门名称的通用处理
    目前部门名称只支持中文和英文，待后续BSM中增加
    """
    def __init__(self, department):
        self.name = department.name
        self.en_name = department.en_name

    def trans(self, lang):
        if lang in ['zh', u'zh']:
            return self.name or ''
        elif lang in ['en', 'ja', u'en', u'ja'] and self.en_name:
            return self.en_name or ''
        else:
            return self.name or ''



