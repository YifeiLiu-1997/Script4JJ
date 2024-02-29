"""
    最新版script代码重构，流程分为几个部分
    1. 直接运行，显示主窗口
        包含了两个自行填写的内容
        ① google sheet 的 url （boss 发来的 google sheet 对应的网址链接）
        ② 需要将项目生成的文件夹  （选择一个空文件夹，会将整个工作项目自动生成到此文件夹下，结构如下：）
            your_folder_name
                ├─all_report （存放 all_report.csv）
                ├─boss_to_me （存放 boss 发来的原始任务文件）
                └─result     （存放两个文件，vlook_ending_file.csv，vlook&processed_ending_file.csv）
    2. 复制 url 和选定项目文件夹后，会显示进度窗口
        包含了进度条以及说明
        ① 进度条显示目前正在处理那个环节（获取 all_report 中，生成 vlook&processing_ending_file 中等）
    3. 当进度条结束，显示看照片页面
"""

import datetime
import os
import sys
import threading
import time
import warnings
from threading import Thread

import pandas as pd
import concat_csv
import downloader

from tkinter import messagebox, Tk, StringVar, Label, Button, Entry, Text, Toplevel, ttk
from tkinter.font import Font
from tkinter.filedialog import askopenfilename, askdirectory
from utils.preprocessing_data import preprocessing_data
from utils.analyser import Wednesday, Thursday, Analyser

warnings.filterwarnings('ignore')


class Main(object):
    def __init__(self):
        self.window = Tk()
        self.ending_show = StringVar()
        self.ending_path = StringVar()
        self.ending_df = None
        self.boss2me_path = StringVar()
        self.boss2me_df = None
        self.all_report_path = StringVar()
        self.all_report_df = None
        self.save_folder_path = StringVar()
        self.result_df = None
        self.version = 'V1.0'
        self.day = None
        self.structured_df = None
        self.message = None
        self.select_box = None

    def _get_ending(self, *args):
        if self.select_box.get() == 'HF F75':
            ending_path = os.getcwd() + '/utils/files/ending_wednesday.csv'
            self.ending_show.set('HF F75')
        else:
            ending_path = os.getcwd() + '/utils/files/ending_thursday.csv'
            self.ending_show.set('others')

        self.ending_path.set(ending_path)
        self.window.update()

    def _get_boss2me(self):
        boss2me_path = askopenfilename()
        self.boss2me_path.set(boss2me_path)
        self.window.update()

    def _get_all_report(self):
        all_report_path = askopenfilename()
        self.all_report_path.set(all_report_path)
        self.window.update()

    def _get_save_folder_path(self):
        save_folder_path = askdirectory()
        self.save_folder_path.set(save_folder_path)
        self.window.update()

    def get_message(self, structured_df, day):
        if day == '3':
            structured_df = structured_df[pd.isna(structured_df['Region Code'])]
        elif day == '4':
            structured_df = structured_df[pd.isna(structured_df['Client'])]

        if structured_df.empty:
            choice = messagebox.askyesno(title='成功', message='没有任何问题，是否继续')
            if choice:
                self.next()
            else:
                return None
        else:
            self.message = Toplevel(master=self.window)
            self.message.geometry('1200x600')
            self.message.title = '有错误'

            # 设置一个 Text
            font = Font(size=16)
            text = Text(self.message, width=80, height=20, font=font)

            date_list = structured_df['Scheduled Delivery Date'].to_list()
            tracking_code_list = structured_df['Tracking Code'].to_list()

            # 创建 dict
            date_dict = {}
            for date in date_list:
                date_dict[date] = []
                for tracking_code in tracking_code_list:
                    date_dict[date].append(tracking_code)

            message = ''
            for date, tracking_list in date_dict.items():
                message += '未搜索到的 tracking_code 为: '
                for tracking_code in tracking_list:
                    message += str(tracking_code) + '/'
                break

            text.pack()
            text.insert('insert', message)

            Button(self.message, text='退出并继续', command=self.next).place(x=600, y=500)
            self.message.mainloop()

    def pre_check(self):
        if self.ending_path.get() == '' or self.boss2me_path.get() == '' or self.all_report_path.get() == '' or \
                self.save_folder_path.get() == '':
            messagebox.showwarning(title='警告', message='有尚未选择的路径')

    def generate_csv(self):
        # 先检查是否选择路径
        self.pre_check()
        self.ending_df = pd.read_csv(self.ending_path.get())
        self.boss2me_df = pd.read_csv(self.boss2me_path.get())
        self.all_report_df = pd.read_csv(self.all_report_path.get())

        # 首先，经过一个筛选函数，将各种客户进行初处理，合并到一起
        structured_df = None
        if 'wednesday' in self.ending_path.get().lower():
            structured_df = preprocessing_data(self.ending_df, self.boss2me_df, self.all_report_df, day='3')
            structured_df = structured_df.rename(columns={'OTD earliest Dropoff Date': 'Scheduled Delivery Date'})
        elif 'thursday' in self.ending_path.get().lower():
            structured_df = preprocessing_data(self.ending_df, self.boss2me_df, self.all_report_df, day='4')
        else:
            messagebox.showinfo(title='错误', message='ending file 有误，请检查')

        # 生成 csv
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        structured_df.to_csv(str(self.save_folder_path.get()) + '/初版' + date_time + '.csv', index=False)
        self.structured_df = structured_df

        # 检查policy有没有错
        if self.policy.get().isnumeric():
            # 开始逐行分析
            if 'thursday' in str(self.ending_path.get()).lower():

                # 如果发现日期没对齐，显示出少了那些日期
                self.day = '4'
                self.get_message(structured_df, day=self.day)

            elif 'wednesday' in str(self.ending_path.get()).lower():
                # 如果发现日期没对齐，显示出少了那些日期
                self.day = '3'
                self.get_message(structured_df, day=self.day)
        else:
            messagebox.showerror(title='policy错误', message='policy填写有误')

    def next(self):
        if self.day == '4':
            thursday = Thursday(self.structured_df, policy=self.policy.get())
            self.result_df = thursday.analyse()

            # 生成 csv
            date_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            self.result_df.drop_duplicates(subset=['Tracking Code'], inplace=True)
            self.result_df.to_csv(str(self.save_folder_path.get()) + '/first' + date_time + '.csv', index=False)

            analyser = Analyser(self.window, self.result_df, self.save_folder_path.get(), '4')
            analyser.run()

        elif self.day == '3':
            # 列名先改一下
            self.structured_df.rename(columns={'Drop off Time': 'Drop off time'}, inplace=True)

            wednesday = Wednesday(self.structured_df, policy=self.policy.get())
            self.result_df = wednesday.analyse()

            # 列名先改回来
            self.result_df.rename(columns={'Drop off time': 'Drop off Time'}, inplace=True)

            # 生成 csv
            res_df = self.result_df.copy()
            try:
                res_df = res_df.drop(columns=['Week#', 'Updated Reason Code'])
            except BaseException:
                pass
            date_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            res_df.drop_duplicates(['Tracking Code'], inplace=True)

            # 2023-11-8 修改列名
            # Scheduled Delivery Date: OTD earliest Dropoff Date
            # Label: Shipment label
            # 删除 Driver Name
            # Courier: Courier name
            res_df.rename(columns={'Scheduled Delivery Date': 'OTD earliest Dropoff Date',
                                   'Label': 'Shipment label',
                                   'Courier': 'Courier name'}, inplace=True)
            res_df.drop(columns=['Driver Name'], inplace=True)
            res_df.to_csv(str(self.save_folder_path.get()) + '/HF first' + date_time + '.csv', index=False)

            analyser = Analyser(self.window, self.result_df, self.save_folder_path.get(), '3')
            analyser.run()

    def concat_all_csv(self):
        concat = concat_csv.Concat(self.window)
        concat.run()

    def open_downloader(self):

        download = downloader.DownLoader(self.window)
        download.run()

    def get_update(self):
        # 获取当前文件夹地址
        current_path = os.getcwd()
        decision = messagebox.askokcancel(title='更新检测', message='是否检测更新？')
        if decision:
            # 开始执行 git pull
            os.popen('cd ' + current_path)
            os.popen('git reset --hard')
            execute = os.popen('git pull')
            for i in range(5):
                time.sleep(2)
                execute_str = execute.read()
                if 'file changed' in execute_str or 'files changed' in execute_str:
                    messagebox.showinfo(title='更新成功', message='更新成功，请重新启动')
                    self.window.destroy()
                    # 打开新的
                    try:
                        sys.exit(0)
                    finally:
                        os.system(os.getcwd() + '/main.py')
                if 'Already up to date' in execute_str:
                    messagebox.showinfo(title='无可用更新', message='无可用更新')
                    return False
            messagebox.showinfo(title='失败', message='更新失败，可能无更新或多次尝试后更新失败')
        else:
            return False

    @staticmethod
    def show_update():

        message = '版本 V2.0\n更新内容:\n'
        message += '''根据最新的2023.3.15版本开发'''
        messagebox.showinfo(
            title='更新内容',
            message=message
        )

    def run(self):
        self.window.title(f'AxleHireTools : version: {self.version}')
        self.window.geometry('850x450')


        # label ending
        self.select_box = ttk.Combobox(
            master=self.window,
            textvariable=self.ending_show
        )
        self.select_box.place(x=100, y=100)
        self.select_box['values'] = ['HF F75', 'others']
        self.select_box.bind("<<ComboboxSelected>>", self._get_ending)

        # label boss2me
        Label(self.window, text="original file:").place(x=100, y=150)
        Entry(self.window, textvariable=self.boss2me_path, width='60').place(x=220, y=150)
        Button(self.window, text="select", command=self._get_boss2me, width='10').place(x=680, y=150)

        # label all_download
        Label(self.window, text="all report file:").place(x=100, y=200)
        Entry(self.window, textvariable=self.all_report_path, width='60').place(x=220, y=200)
        Button(self.window, text="select", command=self._get_all_report, width='10').place(x=680, y=200)

        # label what_you_want
        Label(self.window, text="generate path:").place(x=100, y=250)
        Entry(self.window, textvariable=self.save_folder_path, width='60').place(x=220, y=250)
        Button(self.window, text="select", command=self._get_save_folder_path, width='10').place(x=680, y=250)

        # label policy
        self.policy = StringVar()
        Label(self.window, text="policy:").place(x=100, y=300)
        Entry(self.window, textvariable=self.policy, width='10').place(x=220, y=300)

        # button
        Button(self.window, text='next', width='10', command=self.generate_csv).place(x=680, y=350)
        Button(self.window, text='merge', width='10', command=self.concat_all_csv).place(x=100, y=350)
        Button(self.window, text='download', width='12', command=self.open_downloader).place(x=230, y=350)
        Button(self.window, text='update', width='10', command=self.get_update).place(x=380, y=350)
        Button(self.window, text='update comments', width='15', command=self.show_update).place(x=510, y=350)

        self.window.mainloop()


if __name__ == '__main__':
    main = Main()
    main.run()
