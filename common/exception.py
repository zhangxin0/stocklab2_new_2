# coding: utf-8

class HttpException(Exception):
    def __init__(self, error_code, msg=''):
        Exception.__init__(self, msg)
        self.error_code = error_code


class APIException(HttpException):
    pass


def check(boolean, error_msg):
    if not boolean:
        raise Exception(error_msg)
