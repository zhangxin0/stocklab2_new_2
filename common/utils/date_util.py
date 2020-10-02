# coding:utf-8
# import datetime
from datetime import timedelta, datetime, date
import time

DEFAULT_DATE_FORMAT = '%Y-%m-%d'
POINT_DATE_FORMAT = '%Y.%m.%d'
_DATE_ID_STR = "%Y%m%d"
DATE_TIME_STR = "%Y-%m-%d %H:%M:%S"
DEFAULT_EMPTY_DATE = ''

DEFAULT_DATE = date(2000, 1, 1)
DEFAULT_DATE_TIME = datetime(2000, 1, 1)
HIVE_DATE_FORMAT = '%Y%m%d'
HIVE_DATE_TIME_FORMAT = '%Y%m%d%H%M%S'


class DateUtil(object):

    @staticmethod
    def to_yyyymmdd(datetime_):
        """
        把datetime类型转化为字符串(2018-09-12)
        """
        try:
            date_ = None
            if datetime_:
                date_ = datetime_.strftime(DEFAULT_DATE_FORMAT)

            return date_
        except Exception:
            raise Exception(u'日期%s格式化异常' % datetime_)

    @staticmethod
    def current_date():
        return datetime.now().date()

    @staticmethod
    def date_str_to_millisecond(date_str):
        """
        将日期字符串(YYYY-MM-DD)转化为精确到毫秒级别的13位时间戳字符串
        """
        try:
            time_array = time.strptime(date_str, DEFAULT_DATE_FORMAT)
            return str(int(time.mktime(time_array) * 1000))
        except Exception:
            raise Exception(u'日期%s转换时间戳异常' % date_str)

    @staticmethod
    def hive_str_2date(_date):
        """
        将hive日期格式转化为date
        :param _date:
        :return:
        """
        return datetime.strptime(_date, HIVE_DATE_FORMAT).date()

    @staticmethod
    def date_to_millisecond(_date):
        """
        将日期(YYYY-MM-DD)转化为精确到毫秒级别的13位时间戳字符串
        """
        date_str = _date.strftime(DEFAULT_DATE_FORMAT)
        return DateUtil.date_str_to_millisecond(date_str)

    @staticmethod
    def millisecond_to_date_str(timestamp):
        """
        将精确到毫秒级别的13位时间戳字符串转化为日期字符串(YYYY-MM-DD)
        """
        try:
            time_array = time.localtime(int(timestamp) / 1000)
            return time.strftime(DEFAULT_DATE_FORMAT, time_array)
        except Exception:
            raise Exception(u'时间戳%s转换日期异常' % timestamp)

    @staticmethod
    def future_ten_days():
        return DateUtil.current_date() + timedelta(10)

    @staticmethod
    def future_x_days(days):
        return DateUtil.current_date() + timedelta(days)

    @staticmethod
    def to_specific_pattern(datetime_):
        """
        把datetime类型转化为字符串(2018-09-12)
        """
        try:
            date_ = None
            if datetime_:
                date_ = datetime_.strftime(POINT_DATE_FORMAT)

            return date_
        except Exception:
            raise Exception(u'日期%s格式化异常' % datetime_)

    @staticmethod
    def parse_datetime(datetime_str):
        """
        字符串 2030-12-30 12:00:00 -> datetime
        :param datetime_str:
        :return:
        """
        if not datetime_str:
            return None
        return datetime.strptime(datetime_str, DATE_TIME_STR)

    @staticmethod
    def parse_datetime_str_to_date_str(datetime_str):
        """
        字符串 2030-12-30 12:00:00 -> 字符串 "2030-12-30"
        :param datetime_str:
        :return:
        """
        if not datetime_str:
            return None
        dt = DateUtil.parse_datetime(datetime_str)
        return DateUtil.to_yyyymmdd(dt)

    @staticmethod
    def parse_date_str_to_date(date_str):
        return datetime.strptime(date_str, DEFAULT_DATE_FORMAT).date()

    @staticmethod
    def judge_repeat_period(a_start_date, a_end_date, b_start_date, b_end_date):
        """判断两个输入的时间段，是否有重叠"""
        if not (a_end_date <= b_start_date or b_end_date <= a_start_date):
            return True, u'重叠'
        else:
            return False, u'不重叠'

    @staticmethod
    def is_period_overlap(a_start_date, a_end_date, b_start_date, b_end_date):
        """
        判断时间段重复
        :param a_start_date:
        :param a_end_date:
        :param b_start_date:
        :param b_end_date:
        :return:
        """
        return not (a_end_date < b_start_date or b_end_date < a_start_date)

    @staticmethod
    def format_date(date_time):
        """
        把datetime类型转化为字符串(2018-09-12)
        :param date_time:
        :return:
        """
        if not date_time:
            return ''
        time_strf = date_time.strftime(DEFAULT_DATE_FORMAT)
        if time_strf == '2000-01-01':
            return ''
        return time_strf

    @staticmethod
    def format_time_str(date_time):
        """
        把datetime类型转化为字符串(2018-09-12 12:09:07)
        :param date_time:
        :return:
        """
        if not date_time:
            return ''
        time_strf = date_time.strftime(DATE_TIME_STR)
        if time_strf == '2000-01-01 00:00:00':
            return ''
        return time_strf

    @staticmethod
    def date_2datetime(_date):
        return datetime(_date.year, _date.month, _date.day)

    @staticmethod
    def assert_date(_date):
        """
        保证是 日期格式
        :param _date:
        :return:
        """
        if isinstance(_date, (str, unicode)):
            try:
                _date = datetime.strptime(_date, DEFAULT_DATE_FORMAT)
            except:
                raise
        assert isinstance(_date, date)

    @staticmethod
    def utc0_now():
        return DateUtil.utc_n_now()

    @staticmethod
    def utc8_now():
        return DateUtil.utc_n_now(8)

    @staticmethod
    def utc_n_now(n=0):
        return datetime.utcnow() + timedelta(hours=n)

    @staticmethod
    def get_utc_time(cur_time, hours=0):
        return cur_time + timedelta(hours=hours)




if __name__ == '__main__':
    print(DateUtil.date_str_to_millisecond('2019-01-01'))
    print(DateUtil().date_str_to_millisecond('2019-01-01'))




