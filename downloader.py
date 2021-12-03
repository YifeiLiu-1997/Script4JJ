import os
import datetime
import time
import requests
import json
import pandas as pd
from requests_ntlm import HttpNtlmAuth
from tkinter import Toplevel, Label, Entry, Button, StringVar, messagebox


class DownLoader(object):
    def __init__(self, root=None):
        self.root = root
        self.window = Toplevel(master=self.root)
        self.url = 'https://dataorch.beta.axlehire.com/reports/all/request'
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/95.0.4638.69 Safari/537.36',
            'content-type': 'application/json',
            'cookie': r'fp=1a39e1225ea764ca9f2abf599fafba34; xtoken="dE9DbW1wYkZDI/B28g5MkirtzwljFDty7THWI75r/mVq4do8Y'
                      r'KOJBeUtONSQ1d3L1Yb5JCAEZPTk\012FFj7LXpbKjSaV71j1S6I9zjtTLurIi1ddgqe+xsIRU84cjg0Sktu\012"'
        }
        self.user_name = 'yanxia.ji'
        self.password = 'Axl12345'

    def download_from_url(self, url, file_name):
        print(url)
        # url = 'https://dataorch.beta.axlehire.com/reports/uploaded/8d38816a-98f4-4461-9d4b-1f79cd360e34/download'
        self.make_dir('all_report_history')
        session = requests.Session()
        time.sleep(5)
        response = session.get(url=url, headers=self.header)
        # response = session.get(url=url, headers=self.header)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            print('json_data', json_data)
            response = session.get(url=url+'/download', headers=self.header)
            if 'url' in json_data.keys():
                with open(file_name, 'wb') as fp:
                    fp.write(response.content)
            else:
                self.download_from_url(url, file_name)

        else:
            self.download_from_url(url, file_name)

    def get_csv_from_date(self, client_id, date, file_name):
        session = requests.Session()
        if client_id.find('，') == -1:
            client_id_string = [str(client_id)]
        else:
            client_id_string = client_id.split('，')

        # date
        date = datetime.datetime.strptime(date, '%Y/%m/%d').strftime('%Y-%m-%d')

        json_data = {
            'clients': client_id_string,
            'date': date,
        }

        response = session.post(url=self.url, headers=self.header, json=json_data,
                                auth=HttpNtlmAuth(self.user_name, self.password))
        json_response = json.loads(response.content)
        url = 'https://dataorch.beta.axlehire.com/reports/uploaded/'
        url += json_response['id']
        self.download_from_url(url, file_name)

    def get_date_list(self, from_date, to_date):
        from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d')
        to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d')
        diff = (to_date - from_date).days
        if diff <= 0:
            messagebox.showwarning(title='警告', message='日期范围有误')
        else:
            date_list = [from_date.strftime('%Y/%m/%d')]
            for i in range(1, diff+1):
                date = from_date + datetime.timedelta(days=i)
                date = date.strftime('%Y/%m/%d')
                date_list.append(date)
            return date_list

    @staticmethod
    def make_dir(path):
        if not os.path.exists(path):
            os.mkdir(path)

    def run(self):
        # 初始化界面
        self.window.geometry('700x240')
        self.client = StringVar()
        self.date = StringVar()
        Label(self.window, text='输入 client 号（如有多个，请用，（中文逗号）分隔）:').place(x=50, y=20)
        Entry(self.window, textvariable=self.client).place(x=50, y=60)
        Label(self.window, text='输入日期（形如 2021/11/07 如有多个日期请用,分隔,如果为时间段,请输入形如 2021/11/07-2021/11/09）:')\
            .place(x=50, y=100)
        Entry(self.window, textvariable=self.date).place(x=50, y=140)
        Button(self.window, text='生成 all_report csv', command=self.confirm).place(x=50, y=190)
        self.window.mainloop()

    @staticmethod
    def is_date(date):
        try:
            datetime.datetime.strptime(date, "%Y/%m/%d")
            return True
        except:
            return False

    def confirm(self):
        if self.check_client():
            # date 为 range
            now = datetime.datetime.now().strftime('%m月%d日-%H点%M分%S秒')
            if self.date.get().find('-') != -1:
                date_from_to_list = self.date.get().split('-')
                date_list = self.get_date_list(from_date=date_from_to_list[0], to_date=date_from_to_list[1])
                # 创建文件夹
                folder_name = self.date.get().replace('-', 'to')
                folder_name = folder_name.replace('/', '-')
                folder_name += '&client=' + self.client.get() + '_' + now
                self.make_dir(f'all_report_history/{folder_name}')
                for date in date_list:
                    date_name = date.replace('/', '-')
                    self.get_csv_from_date(
                        client_id=self.client.get(),
                        date=date,
                        file_name=f'all_report_history/{folder_name}/client={self.client.get()}&date='f'{date_name}&{now}.csv'
                    )
                self.concat_from_folder(f'all_report_history/{folder_name}')
            # 单个date
            elif self.is_date(self.date.get()):
                date = datetime.datetime.strptime(self.date.get(), '%Y/%m/%d').strftime('%Y-%m-%d')
                self.get_csv_from_date(
                    client_id=self.client.get(),
                    date=self.date.get(),
                    file_name=f'all_report_history/client={self.client.get()}&date={date}&{now}.csv'
                )
            else:
                messagebox.showwarning(title='警告', message='日期格式有误')
        else:
            messagebox.showwarning(title='警告', message='client格式有误')

    def check_client(self):
        # client 是单个
        if self.client.get().find('，') == -1:
            if not self.client.get().isnumeric():
                return False
            # 是数字
            else:
                if int(self.client.get()) <= 11 or int(self.client.get()) == 471 or int(self.client.get()) == 621 \
                        or (int(self.client.get()) >= 15 and int(self.client.get()) <= 214):
                    return True
                return False
        # client 是多个
        else:
            client_list = self.client.get().split('，')
            for client in client_list:
                if client.find('，') == -1:
                    if not client.isnumeric():
                        return False
                    # 是数字
                    else:
                        if int(client) <= 214 or int(client) == 471 or int(client) == 621:
                            return True
                        return False

    @staticmethod
    def get_dict_from_tracking_code(tracking_code):
        url = 'https://dataorch.axlehire.com/shipments/search'
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'content-type': 'application/json',
            'cookie': r'fp=1a39e1225ea764ca9f2abf599fafba34; xtoken="dE9DbW1wYkZDI/B28g5MkirtzwljFDty7THWI75r/mVq4do8YKOJBeUtONSQ1d3L1Yb5JCAEZPTk\012FFj7LXpbKjSaV71j1S6I9zjtTLurIi1ddgqe+xsIRU84cjg0Sktu\012"'}
        # 生成 post 的 json_data
        data_dict = {'size': 15, 'q': tracking_code,
                     'filters': {}, 'sorts': ['-dropoff_earliest_ts']}
        json_data = json.dumps(data_dict)

        session = requests.Session()
        user = 'yanxia.ji'
        password = 'Axl12345'
        response = session.post(url=url, headers=header, data=json_data, auth=HttpNtlmAuth(user, password))

        result_dict = json.loads(response.text)
        return result_dict

    @staticmethod
    def concat_from_folder(folder_path):
        dir_list = os.listdir(folder_path)
        res_df = pd.DataFrame()
        for file in dir_list:
            file_path = folder_path + '/' + file
            temp_df = pd.read_csv(file_path)
            res_df = pd.concat([res_df, temp_df])
        res_df.to_csv(folder_path + '/all.csv', index=False)
        path = folder_path + '/all.csv'
        messagebox.showinfo(title='成功', message=f'输出路径为: {path}')
        return res_df


if __name__ == '__main__':
    downloader = DownLoader()
    # downloader.get_csv_from_date(client_id='159', date='2021-10-19')2021-10-19
    # print(downloader.get_dict_from_tracking_code('SCD1970110400304388'))
    # downloader.get_csv_from_date(
    #     client_id=['49'],
    #     date='2021-11-17',
    #     file_name='ff.csv'
    # )
    # downloader.download_from_url(url='https://dataorch.beta.axlehire.com/reports/uploaded/f705aa7f-6b32-4868-9892-5fb9ab6e138d', file_name='ff')
    # st = '2021/11/17'
    # s = str(int(datetime.datetime.strptime(st, '%Y/%m/%d').timestamp()))
    # print(s)
    downloader.run()
