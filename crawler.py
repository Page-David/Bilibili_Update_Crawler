#!/usr/bin/env python3
import requests
import time
import subprocess
import os
import sys
import ast
import threading

# 視頻信息地址，UP主空間號待填
JSON_URL = 'http://space.bilibili.com/ajax/member/getSubmitVideos?mid={}&pagesize=30&tid=0&keyword=&page=1'
# 刷新間隔時間
REFRESH_TIME = 5

class Crawler(object):
    
    def __init__(self, code):
        self.url = JSON_URL.format(code)
        self.time = REFRESH_TIME * 59 # 秒 -> 分鍾
        self.code = code # UP主空間號 
        self.response = None
        self.filename = '.{}.json'.format(self.code) 
        self.current_json = dict()

    def start(self):
        # 檢查是否存在視頻列表文件
        if not self.filename in os.listdir():
            self.request_json()
            self.save_json()
            self.read_json()
        else:
            self.read_json()
        print('初始化完畢')
        # 啓動循環
        threading.Thread(target=self.worker).start()

    def worker(self):
        while True:
            self._worker()

    def _worker(self):
        time.sleep(self.time)
        self.request_json()
        print('新的請求發送成功。')
        diff = self._list_diff(self.response.json()['data']['vlist'],\
                               self.current_json
                               )
        self.current_json = self.response.json()['data']['vlist']
        print('UP主給你欽點了{}個視頻'.format(len(diff)))
        for d in diff:
            self.send_notif(d)
        self.save_json()


    def request_json(self):
        try:
            self.response = requests.get(self.url)
        except Exception as e:
            print(e)
            print("網絡錯誤，看來你的網絡還too young。")
            sys.exit(2)

    def save_json(self):
        with open(self.filename, 'w') as json_f:
            json_f.write(str(self.response.json()['data']['vlist']))
            
    def read_json(self):
        with open(self.filename, 'r') as json_f:
            self.current_json = ast.literal_eval(json_f.read())

    def _list_diff(self, new, old):
        return [sth for sth in new if not sth in old]

    def send_notif(self, data):
        subprocess.call(['notify-send', data['title'], data['description']])

def main():
    crawler = Crawler(sys.argv[1])
    crawler.start()
    print('不想用了按Ctrl+c，識得唔識得啊？？')

if __name__ == '__main__':
    main()
