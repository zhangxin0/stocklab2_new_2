# -*- coding: utf-8 -*-
from decimal import Decimal


class NumberUtil(object):
    """
    数字工具类
    """

    @staticmethod
    def retain_decimal(num, ndigits=2):
        """
        保留2位小数
        :param num:
        :param ndigits:
        :return:
        """
        if not num:
            return num
        if isinstance(num, int):
            return num
        if isinstance(num, float):
            return round(num, ndigits=ndigits)
        if isinstance(num, Decimal):
            return num.quantize(Decimal('0.00'))
        return num

    @staticmethod
    def hive_cost_transfer(cost):
        """
        数仓10w -》元
        :param cost:
        :return:
        """
        return cost / Decimal(100000)

    @staticmethod
    def retail_str(num, ndigits=2):
        """
        2位小数，返回str
        :param num:
        :param ndigits:
        :return:
        """
        return ('%.' + str(ndigits) + 'f') % num


if __name__ == '__main__':
    print(NumberUtil.retain_decimal(Decimal(100.111)))