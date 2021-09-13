# -*- coding: UTF-8 -*-
# python
import json
import urllib.request

class Message():
    def notify(self, symbol, operation, phone):
        msg = 'usernm%3Dadmin%26code%3D' + symbol + '-' + operation
        url = f"https://sapi.k780.com/?app=sms.send&tplId=51819&tplParam={msg}&phone={phone}&appkey=47217&sign=94fdf05b264ee3cef0794fd2aa3cacd9"
        f = urllib.request.urlopen(url)
        nowapi_call = f.read()
        # print content
        a_result = json.loads(nowapi_call)
        if a_result:
            if a_result['success'] != '0':
                print(a_result['result'])
            else:
                print(a_result['msgid'] + ' ' + a_result['msg'])
        else:
            print('Request nowapi fail.')
