"""
    疯狂 work project
    1. 首先，手动下载 boss 传给我的链接中，boss2me file 和对应的 all_report，利用周三周四需要提交的模板，此三个文件，共同初始化出一个文件
        a. 将重命名后的 boss2me，进行第一步分析，通过文件名过滤出各家顾客的名单，走入不同的流程
        b. 更改各家对应的名称，与 all_report 进行 merge，生成相同的 structured_dataframe
    2. 其次，将生成的初版 dataframe 进行分析，返回分析后的 dataframe
        a. 逐行分析，遇到相应的错误，将可以复制的三列复制
        b. （未来）：逐行分析的时候，提供可观看的列以及 tracking code 对应的照片，并询问原因，当填入的时候，根据填的内容，复制新的值到 dataframe
"""

import datetime
import os
import sys
import time

import pandas as pd
import concat_csv

from tkinter import messagebox, Tk, StringVar, Label, Button, Entry, Text, Toplevel
from tkinter.font import Font
from tkinter.filedialog import askopenfilename, askdirectory
from utils.preprocessing_data import preprocessing_data
from utils.analyser import Wednesday, Thursday, Analyser


class Main(object):
    def __init__(self):
        self.window = Tk()
        self.ending_path = StringVar()
        self.ending_df = None
        self.boss2me_path = StringVar()
        self.boss2me_df = None
        self.all_report_path = StringVar()
        self.all_report_df = None
        self.save_folder_path = StringVar()
        self.result_df = None
        self.version = 'v1.11.24.01'
        self.day = None
        self.structured_df = None
        self.message = None

    def _get_ending(self):
        ending_path = askopenfilename()
        self.ending_path.set(ending_path)
        self.window.update()
        # self.ending_path = self.ending_path.get()
        # self.ending_df = pd.read_csv(self.ending_path)

    def _get_boss2me(self):
        boss2me_path = askopenfilename()
        self.boss2me_path.set(boss2me_path)
        self.window.update()
        # self.boss2me_path = self.boss2me_path.get()
        # self.boss2me_df = pd.read_csv(self.boss2me_path)

    def _get_all_report(self):
        all_report_path = askopenfilename()
        self.all_report_path.set(all_report_path)
        self.window.update()
        # self.all_report_path = self.all_report_path.get()
        # self.all_report_df = pd.read_csv(self.all_report_path)

    def _get_save_folder_path(self):
        save_folder_path = askdirectory()
        self.save_folder_path.set(save_folder_path)
        self.window.update()
        # self.save_folder_path = self.save_folder_path.get()

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

            print(date_dict)

            message = ''
            for date, tracking_list in date_dict.items():
                message += date + ', tracking_code 为: '
                for tracking_code in tracking_list:
                    message += tracking_code + '/'
                message += '\n\n'

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
            structured_df = structured_df.rename(columns={'delivery_date': 'Scheduled Delivery Date'})
        elif 'thursday' in self.ending_path.get().lower():
            structured_df = preprocessing_data(self.ending_df, self.boss2me_df, self.all_report_df, day='4')
        else:
            messagebox.showinfo(title='错误', message='ending file 有误，请检查')

        # 生成 csv
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        structured_df.to_csv(str(self.save_folder_path.get()) + '/初版' + date_time + '.csv', index=False)
        self.structured_df = structured_df

        # 开始逐行分析已经结构化的 dataframe，通过老板发的，（行要一致）
        if 'thursday' in str(self.ending_path.get()).lower():
            # 如果发现日期没对齐，显示出少了那些日期
            self.day = '4'
            self.get_message(structured_df, day=self.day)

        elif 'wednesday' in str(self.ending_path.get()).lower():
            # 如果发现日期没对齐，显示出少了那些日期
            self.day = '3'
            self.get_message(structured_df, day=self.day)

    def next(self):
        if self.day == '4':
            thursday = Thursday(self.structured_df)
            self.result_df = thursday.analyse()

            # 生成 csv
            date_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            self.result_df.to_csv(str(self.save_folder_path.get()) + '/first' + date_time + '.csv', index=False)

            analyser = Analyser(self.window, self.result_df, self.save_folder_path.get(), '4')
            analyser.run()

        elif self.day == '3':
            # 周三的一些列名先改一下
            self.structured_df.rename(columns={'Drop off Time': 'Drop off time'}, inplace=True)

            wednesday = Wednesday(self.structured_df)
            self.result_df = wednesday.analyse()

            # 周三的一些列名先改回来
            self.result_df.rename(columns={'Drop off time': 'Drop off Time'}, inplace=True)

            # 生成 csv
            res_df = self.result_df.copy()
            res_df = res_df.drop(columns=['Week#', 'Updated Reason Code'])
            date_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            res_df.to_csv(str(self.save_folder_path.get()) + '/HF first' + date_time + '.csv', index=False)

            analyser = Analyser(self.window, self.result_df, self.save_folder_path.get(), '3')
            analyser.run()

    def concat_all_csv(self):
        concat = concat_csv.Concat(self.window)
        concat.run()

    def get_update(self):
        # 获取当前文件夹地址
        current_path = os.getcwd()
        print(current_path)
        decision = messagebox.askokcancel(title='更新检测', message='是否检测更新？')
        print(decision)
        if decision:
            # 开始执行 git pull
            os.popen('cd ' + current_path)
            os.popen('git reset --hard')
            execute = os.popen('git pull')
            for i in range(5):
                time.sleep(2)
                # execute_str = ''
                # if execute.readlines() != []:
                #     execute_str = execute.readlines()[0]
                # print(execute_str)
                execute_str = execute.read()
                print(execute_str)
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
        # v1.11.13
        message = '版本 v1.11.13\n更新内容:\n1. Mailroom/lobby 转为人工判断'
        # v1.11.13.01
        message += '\n\n版本 v1.11.13.01\n更新内容:\n1. 解决 POD 存在 nan 的情况'
        # v1.11.13.02
        message += '\n\n版本 v1.11.13.02\n更新内容:\n1. 增加更新状态，“无可用更新”'
        # v1.11.24.01
        message += '\n\n版本 v1.11.24.01\n更新内容:\n'
        message += '''- 修复若干功能
    1. 修复了如有多张照片，则会显示多张照片
    2. 修复了在点击 next 的时候，检查窗口关闭无法继续的 bug，改为手动选择是否继续
    3. 修复了合并界面不显示路径的 bug 
- 新增若干功能
    1. 新增清除缓存时，显示实际清除缓存的内存 
    2. 新增当 ending file 选错时的提示 
    3. 新增当合并 ending, boss2me, all_report 不全的提示界面，点击继续可无视缺失继续 '''

        messagebox.showinfo(
            title='更新内容',
            message=message
        )

    def run(self):
        self.window.title(f'♥ Only For JJ ♥ : version: {self.version}')
        self.window.geometry('850x400')
        # self.wrong_message = StringVar()

        # label ending
        Label(self.window, text="ending file:").place(x=100, y=100)
        Entry(self.window, textvariable=self.ending_path, width='60').place(x=220, y=100)
        Button(self.window, text="select", command=self._get_ending, width='10').place(x=680, y=100)

        # label boss2me
        Label(self.window, text="boss2me file:").place(x=100, y=150)
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

        # button
        Button(self.window, text='next', width='10', command=self.generate_csv).place(x=680, y=300)
        Button(self.window, text='merge', width='12', command=self.concat_all_csv).place(x=100, y=300)
        Button(self.window, text='update', width='12', command=self.get_update).place(x=295, y=300)
        Button(self.window, text='update comments', width='18', command=self.show_update).place(x=470, y=300)

        self.window.mainloop()


if __name__ == '__main__':
    main = Main()
    main.run()
