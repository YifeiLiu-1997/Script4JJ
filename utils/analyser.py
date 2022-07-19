import json
import os
import shutil
import pandas as pd
import utils.analyser_utils as analyser_utils
import requests
import cv2.cv2 as cv2
import datetime

from tkinter import ttk, Button, messagebox, StringVar, Label, Entry, Toplevel
from requests_ntlm import HttpNtlmAuth


class Analyser(object):
    def __init__(self, root, first_analysed_df, save_path, day):
        self.root = root
        self.source_df = first_analysed_df.reset_index(drop=True)
        self.data_frame = self.initialize_df(first_analysed_df)
        self.window = None
        self.temp_window = None
        self.url = 'https://dataorch.axlehire.com/shipments/search'
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'content-type': 'application/json',
            'cookie': r'fp=1a39e1225ea764ca9f2abf599fafba34; xtoken="dE9DbW1wYkZDI/B28g5MkirtzwljFDty7THWI75r/mVq4do8YKOJBeUtONSQ1d3L1Yb5JCAEZPTk\012FFj7LXpbKjSaV71j1S6I9zjtTLurIi1ddgqe+xsIRU84cjg0Sktu\012"'}
        self.index = 0
        self.save_folder_path = save_path
        self.day = day
        self.mission_length = len(self.data_frame['Tracking Code'])

    def initialize_param_dict(self):
        # 周四
        if self.day == '4':
            param_dict = {'Reason for Complaint': StringVar(), 'Details of Complaint': StringVar(),
                          'Tracking Code': StringVar(), 'Drop off status': StringVar(),
                          'Earliest Dropoff Time': StringVar(), 'Latest Dropoff Time': StringVar(),
                          'Scheduled Delivery Date': StringVar(), 'Shipment status': StringVar(),
                          'Inbound Scan Date 减 Scheduled Delivery Date': StringVar(),
                          'Inbound Scan Date (Linehaul)': StringVar(), 'Inbound Scan Time': StringVar(),
                          'Inbound status': StringVar(), 'Pickup Date 减 Scheduled Delivery Date': StringVar(),
                          'Pickup Date': StringVar(), 'Pickup Time': StringVar(), 'Pickup Status': StringVar(),
                          'Drop off date 减 Pickup Date': StringVar(), 'Drop off date': StringVar(),
                          'Drop off time': StringVar(), 'Drop off remark': StringVar()}
            return param_dict
        # 周三
        elif self.day == '3':
            param_dict = {'Tracking Code': StringVar(), 'Drop off status': StringVar(),
                          'Earliest Dropoff Time': StringVar(), 'Latest Dropoff Time': StringVar(),
                          'Scheduled Delivery Date': StringVar(), 'Shipment status': StringVar(),
                          'Inbound Scan Date 减 Scheduled Delivery Date': StringVar(),
                          'Inbound Scan Date (Linehaul)': StringVar(), 'Inbound Scan Time': StringVar(),
                          'Inbound status': StringVar(), 'Pickup Date 减 Scheduled Delivery Date': StringVar(),
                          'Pickup Date': StringVar(), 'Pickup Time': StringVar(), 'Pickup Status': StringVar(),
                          'Drop off date 减 Pickup Date': StringVar(), 'Drop off date': StringVar(),
                          'Drop off Time': StringVar(), 'Drop off remark': StringVar()}
            return param_dict

    @staticmethod
    def initialize_df(first_df):
        """
        取一切需要打标签的内容
        包含：drop off status == 'Success' 的情况
        Issue Category 为空的情况 （没填上）
        """
        first_df['Inbound Scan Date 减 Scheduled Delivery Date'] = None
        first_df['Pickup Date 减 Scheduled Delivery Date'] = None
        first_df['Pickup Date 减 Drop off date'] = None
        for index, row in first_df.iterrows():
            first_df.loc[index, 'Inbound Scan Date 减 Scheduled Delivery Date'] \
                = analyser_utils.date_subtract(first_df.loc[index, 'Inbound Scan Date (Linehaul)'],
                                               first_df.loc[index, 'Scheduled Delivery Date'])
            first_df.loc[index, 'Pickup Date 减 Scheduled Delivery Date'] \
                = analyser_utils.date_subtract(first_df.loc[index, 'Pickup Date'],
                                               first_df.loc[index, 'Scheduled Delivery Date'])
            first_df.loc[index, 'Drop off date 减 Pickup Date'] \
                = analyser_utils.date_subtract(first_df.loc[index, 'Drop off date'],
                                               first_df.loc[index, 'Pickup Date'])
        first_df_up = first_df[first_df['Drop off status'] == 'SUCCEEDED']
        first_df_down = first_df[pd.isna(first_df['Issue Category'])]
        res_df = pd.concat([first_df_up, first_df_down]).drop_duplicates().reset_index(drop=True)
        return res_df

    def run(self):
        """
        run 的逻辑
        再此创建一个新的 tkinter 界面，并提供两个按钮，上一页，下一页
        上一页 依然运行 run 函数，只不过 self.index + 1
        """
        # 一堆逻辑 列出当前 index 的 dataframe，周四
        # 周四
        if self.day == '4':
            self.window = Toplevel(master=self.root)
            self.param_dict = self.initialize_param_dict()
            self.temp_window = ttk.Treeview(self.window, show='headings')
            # 加入各种列
            self.temp_window['columns'] = ('Reason for Complaint', 'Details of Complaint', 'Tracking Code',
                                           'Drop off status', 'Earliest dropoff time', 'Latest dropoff time',
                                           'Scheduled Date', 'Shipment status', 'Inbound 减 Scheduled', 'Inbound Date',
                                           'Inbound scan time', 'Inbound status', 'Pickup 减 Scheduled', 'Pickup Date',
                                           'Pickup Time', 'Pickup status',
                                           'Drop off 减 Pickup', 'Drop off date', 'Drop off time', 'Drop off remark')

            self.temp_window.column('Reason for Complaint', width=65)
            self.temp_window.column('Details of Complaint', width=65)
            self.temp_window.column('Tracking Code', width=100)
            self.temp_window.column('Drop off status', width=100)
            self.temp_window.column('Earliest dropoff time', width=50)  #
            self.temp_window.column('Latest dropoff time', width=50)  #
            self.temp_window.column('Scheduled Date', width=90)
            self.temp_window.column('Shipment status', width=80)  #
            self.temp_window.column('Inbound 减 Scheduled', width=40)
            self.temp_window.column('Inbound Date', width=80)
            self.temp_window.column('Inbound scan time', width=50)  #
            self.temp_window.column('Inbound status', width=80)  #
            self.temp_window.column('Pickup 减 Scheduled', width=40)
            self.temp_window.column('Pickup Date', width=90)
            self.temp_window.column('Pickup Time', width=65)
            self.temp_window.column('Pickup status', width=65)  #
            self.temp_window.column('Drop off 减 Pickup', width=40)
            self.temp_window.column('Drop off date', width=65)
            self.temp_window.column('Drop off time', width=65)
            self.temp_window.column('Drop off remark', width=120)

            self.temp_window.heading('Reason for Complaint', text='Reason for Complaint')
            self.temp_window.heading('Details of Complaint', text='Details of Complaint')
            self.temp_window.heading('Tracking Code', text='Tracking Code')
            self.temp_window.heading('Drop off status', text='Drop off status')
            self.temp_window.heading('Earliest dropoff time', text='Earliest dropoff time')
            self.temp_window.heading('Latest dropoff time', text='Latest dropoff time')
            self.temp_window.heading('Scheduled Date', text='Scheduled Date')
            self.temp_window.heading('Shipment status', text='Shipment status')
            self.temp_window.heading('Inbound 减 Scheduled', text='Inbound 减 Scheduled')
            self.temp_window.heading('Inbound Date', text='Inbound Date')
            self.temp_window.heading('Inbound scan time', text='Inbound scan time')
            self.temp_window.heading('Inbound status', text='Inbound status')
            self.temp_window.heading('Pickup 减 Scheduled', text='Pickup 减 Scheduled')
            self.temp_window.heading('Pickup Date', text='Pickup Date')
            self.temp_window.heading('Pickup Time', text='Pickup Time')
            self.temp_window.heading('Pickup status', text='Pickup status')
            self.temp_window.heading('Drop off 减 Pickup', text='Drop off 减 Pickup')
            self.temp_window.heading('Drop off date', text='Drop off date')
            self.temp_window.heading('Drop off time', text='Drop off time')
            self.temp_window.heading('Drop off remark', text='Drop off remark')

            # 初次设置值
            self.change_data(data_index=0)
            self.temp_window.pack(pady=20)

            # button_next 的函数为 next_page
            prev_button = Button(self.window, text='上一页', command=self.prev_page)
            prev_button.place(x=100, y=100)

            next_button = Button(self.window, text='下一页', command=self.next_page)
            next_button.place(x=300, y=100)

            confirm_button = Button(self.window, text='确定', command=self.confirm)
            confirm_button.place(x=900, y=100)

            Button(self.window, text='清除缓存', command=self.clear_cache).place(x=1200, y=100)
            Button(self.window, text='显示照片', command=self.show_pic).place(x=1100, y=100)
            Button(self.window, text='提交', command=self.hand_in_result).place(x=1300, y=100)
            Button(self.window, text='打开字典', command=self.open_dictionary).place(x=1300, y=200)
            
            # 显示进度
            self.process = StringVar()
            Entry(self.window, width='10', textvariable=self.process).place(x=100, y=300)
            self.process.set(str(self.index) + '/' + str(self.mission_length))
            
            # 绑定按键
            self.window.bind('<Down>', self.next_page)
            self.window.bind('<Up>', self.prev_page)
            self.window.bind('<Return>', self.confirm)
            self.window.bind('<s>', self.show_pic)

            # 设置一个框，用于填对应的序号
            self.answer = StringVar()
            Label(self.window, text="此条记录的问题，对应的 JJ 序号:").place(x=500, y=100)
            Entry(self.window, width='5', textvariable=self.answer).place(x=720, y=100)

            # 显示 tracking code
            self.tracking_code = StringVar()
            Label(self.window, text="Tracking code:").place(x=600, y=200)
            Entry(self.window, width='20', textvariable=self.tracking_code).place(x=700, y=200)
            self.tracking_code.set(self.data_frame.loc[self.index, 'Tracking Code'])

            # 显示 顾客的 notes
            self.client_comment = StringVar()
            Label(self.window, text="note:").place(x=100, y=150)
            Entry(self.window, width='100', textvariable=self.client_comment).place(x=150, y=150)
            result_dict = self.get_dict_from_tracking_code(
                tracking_code=self.data_frame.loc[self.index, 'Tracking Code']
            )
            if 'dropoff_note' in result_dict['results'][0]['shipment'].keys():
                self.client_comment.set(result_dict['shipment']['dropoff_note'])
            else:
                self.client_comment.set('')

            # 显示 customer id
            self.customer_id = StringVar()
            Label(self.window, text="note:").place(x=800, y=150)
            Entry(self.window, width='100', textvariable=self.customer_id).place(x=900, y=150)
            if 'customer' in result_dict['results'][0]['shipment'].keys():
                self.customer_id.set(result_dict['shipment']['customer']['phone_number'])
            else:
                self.customer_id.set('')

            # 一堆逻辑 显示出图片和详细地址文字
            self.window.mainloop()

        # 周三
        elif self.day == '3':
            self.window = Toplevel(master=self.root)
            self.param_dict = self.initialize_param_dict()
            self.temp_window = ttk.Treeview(self.window, show='headings')
            # 加入各种列
            self.temp_window['columns'] = ('Tracking Code',
                                           'Drop off status',
                                           'Scheduled Date', 'Earliest Dropoff Time', 'Latest Dropoff Time',
                                           'Shipment status', 'Inbound 减 Scheduled', 'Inbound Date',
                                           'Inbound scan time', 'Inbound status', 'Pickup 减 Scheduled', 'Pickup Date',
                                           'Pickup Time', 'Pickup status',
                                           'Drop off 减 Pickup', 'Drop off date', 'Drop off Time', 'Drop off remark')

            self.temp_window.column('Tracking Code', width=100)
            self.temp_window.column('Drop off status', width=100)
            self.temp_window.column('Scheduled Date', width=120)
            self.temp_window.column('Earliest Dropoff Time', width=50)  #
            self.temp_window.column('Latest Dropoff Time', width=50)  #
            self.temp_window.column('Shipment status', width=120)  #
            self.temp_window.column('Inbound 减 Scheduled', width=40)
            self.temp_window.column('Inbound Date', width=120)
            self.temp_window.column('Inbound scan time', width=80)  #
            self.temp_window.column('Inbound status', width=80)  #
            self.temp_window.column('Pickup 减 Scheduled', width=40)
            self.temp_window.column('Pickup Date', width=50)
            self.temp_window.column('Pickup Time', width=50)
            self.temp_window.column('Pickup status', width=120)  #
            self.temp_window.column('Drop off 减 Pickup', width=40)
            self.temp_window.column('Drop off date', width=100)
            self.temp_window.column('Drop off Time', width=50)
            self.temp_window.column('Drop off remark', width=120)

            self.temp_window.heading('Tracking Code', text='Tracking Code')
            self.temp_window.heading('Drop off status', text='Drop off status')
            self.temp_window.heading('Scheduled Date', text='Scheduled Date')
            self.temp_window.heading('Earliest Dropoff Time', text='Earliest dropoff Time')
            self.temp_window.heading('Latest Dropoff Time', text='Latest dropoff Time')
            self.temp_window.heading('Shipment status', text='Shipment status')
            self.temp_window.heading('Inbound 减 Scheduled', text='Inbound 减 Scheduled')
            self.temp_window.heading('Inbound Date', text='Inbound Date')
            self.temp_window.heading('Inbound scan time', text='Inbound scan time')
            self.temp_window.heading('Inbound status', text='Inbound status')
            self.temp_window.heading('Pickup 减 Scheduled', text='Pickup 减 Scheduled')
            self.temp_window.heading('Pickup Date', text='Pickup Date')
            self.temp_window.heading('Pickup Time', text='Pickup Time')
            self.temp_window.heading('Pickup status', text='Pickup status')
            self.temp_window.heading('Drop off 减 Pickup', text='Drop off 减 Pickup')
            self.temp_window.heading('Drop off date', text='Drop off date')
            self.temp_window.heading('Drop off Time', text='Drop off Time')
            self.temp_window.heading('Drop off remark', text='Drop off remark')

            # 初次设置值
            self.change_data(data_index=0)
            self.temp_window.pack(pady=20)

            # button_next 的函数为 next_page
            prev_button = Button(self.window, text='上一页', command=self.prev_page)
            prev_button.place(x=100, y=100)

            next_button = Button(self.window, text='下一页', command=self.next_page)
            next_button.place(x=300, y=100)

            confirm_button = Button(self.window, text='确定', command=self.confirm)
            confirm_button.place(x=900, y=100)
            Button(self.window, text='清除缓存', command=self.clear_cache).place(x=1200, y=100)
            Button(self.window, text='显示照片', command=self.show_pic).place(x=1100, y=100)
            Button(self.window, text='提交', command=self.hand_in_result).place(x=1300, y=100)
            Button(self.window, text='打开字典', command=self.open_dictionary).place(x=1300, y=200)
            
            # 显示进度
            self.process = StringVar()
            Entry(self.window, width='10', textvariable=self.process).place(x=100, y=300)
            self.process.set(str(self.index) + '/' + str(self.mission_length))
            
            # 绑定按键
            self.window.bind('<Down>', self.next_page)
            self.window.bind('<Up>', self.prev_page)
            self.window.bind('<Return>', self.confirm)
            self.window.bind('<s>', self.show_pic)

            # 设置一个框，用于填对应的序号
            self.answer = StringVar()
            Label(self.window, text="此条记录的问题，对应的 JJ 序号:").place(x=500, y=100)
            entry = Entry(self.window, width='5', textvariable=self.answer).place(x=720, y=100)

            # 显示 tracking code
            self.tracking_code = StringVar()
            Label(self.window, text="Tracking Code:").place(x=600, y=200)
            Entry(self.window, width='20', textvariable=self.tracking_code).place(x=700, y=200)
            self.tracking_code.set(self.data_frame.loc[self.index, 'Tracking Code'])

            # 显示 顾客的 notes
            self.client_comment = StringVar()
            Label(self.window, text="note:").place(x=100, y=150)
            Entry(self.window, width='100', textvariable=self.client_comment).place(x=150, y=150)
            result_dict = self.get_dict_from_tracking_code(
                tracking_code=self.data_frame.loc[self.index, 'Tracking Code']
            )
            if 'dropoff_note' in result_dict['results'][0]['shipment'].keys():
                self.client_comment.set(result_dict['results'][0]['shipment']['dropoff_note'])
            else:
                self.client_comment.set('')

            # 显示 customer id
            self.customer_id = StringVar()
            Label(self.window, text="note:").place(x=800, y=150)
            Entry(self.window, width='100', textvariable=self.customer_id).place(x=900, y=150)
            if 'customer' in result_dict['results'][0]['shipment'].keys():
                self.customer_id.set(result_dict['shipment']['customer']['phone_number'])
            else:
                self.customer_id.set('')
                
            # 进度条
            self.process.set(str(self.index) + '/' + str(self.mission_length))
            
            # 一堆逻辑 显示出图片和详细地址文字
            self.window.mainloop()

    def next_page(self, event=None):
        self.index = self.index + 1
        
        if self.index >= len(self.data_frame['Tracking Code']):
            # 到达最底下了
            messagebox.showinfo(title='警告', message='没有下一页了')
            self.window.focus_force()
            self.index = self.index - 1
            self.change_data(self.index)
            
        self.change_data(self.index)
        
        # tracing code
        self.tracking_code.set(self.data_frame.loc[self.index, 'Tracking Code'])
        
        # dropoff note
        result_dict = self.get_dict_from_tracking_code(
            tracking_code=self.data_frame.loc[self.index, 'Tracking Code']
        )
        if 'dropoff_note' in result_dict['results'][0]['shipment'].keys():
            self.client_comment.set(result_dict['results'][0]['shipment']['dropoff_note'])
        else:
            self.client_comment.set('')
        
        # customer_id
        self.customer_id = StringVar()
        if 'customer' in result_dict['results'][0]['shipment'].keys():
            self.customer_id.set(result_dict['shipment']['customer']['phone_number'])
        else:
            self.customer_id.set('')
        
        # 进度条
        self.process.set(str(self.index) + '/' + str(self.mission_length))
        
        self.temp_window.delete(f'item{self.index - 1}')

    def prev_page(self, event=None):
        self.index = self.index - 1
        if self.index < 0:
            # 到达最开始了
            messagebox.showinfo(title='警告', message='没有上一页了')
            self.window.focus_force()
            self.index = self.index + 1
            self.change_data(self.index)
            
        self.change_data(self.index)
        
        # tracing code
        self.tracking_code.set(self.data_frame.loc[self.index, 'Tracking Code'])

        # dropoff note
        result_dict = self.get_dict_from_tracking_code(
            tracking_code=self.data_frame.loc[self.index, 'Tracking Code']
        )
        if 'dropoff_note' in result_dict['results'][0]['shipment'].keys():
            self.client_comment.set(result_dict['results'][0]['shipment']['dropoff_note'])
        else:
            self.client_comment.set('')

        # customer_id
        self.customer_id = StringVar()
        if 'customer' in result_dict['results'][0]['shipment'].keys():
            self.customer_id.set(result_dict['shipment']['customer']['phone_number'])
        else:
            self.customer_id.set('')
            
        self.temp_window.delete(f'item{self.index + 1}')

    def change_data(self, data_index):
        # 设置 StringVar
        if self.day == '4':
            self.param_dict['Reason for Complaint'].set(self.data_frame.loc[data_index, 'Reason for Complaint'])
            self.param_dict['Details of Complaint'].set(self.data_frame.loc[data_index, 'Details of Complaint'])
            self.param_dict['Tracking Code'].set(self.data_frame.loc[data_index, 'Tracking Code'])
            self.param_dict['Drop off status'].set(self.data_frame.loc[data_index, 'Drop off status'])
            self.param_dict['Earliest Dropoff Time'].set(self.data_frame.loc[data_index, 'Earliest Dropoff Time'])
            self.param_dict['Latest Dropoff Time'].set(self.data_frame.loc[data_index, 'Latest Dropoff Time'])
            self.param_dict['Scheduled Delivery Date'].set(self.data_frame.loc[data_index, 'Scheduled Delivery Date'])
            self.param_dict['Shipment status'].set(self.data_frame.loc[data_index, 'Shipment status'])
            self.param_dict['Inbound Scan Date 减 Scheduled Delivery Date'].set(
                self.data_frame.loc[data_index, 'Inbound Scan Date 减 Scheduled Delivery Date'])
            self.param_dict['Inbound Scan Date (Linehaul)'].set(
                self.data_frame.loc[data_index, 'Inbound Scan Date (Linehaul)'])
            self.param_dict['Inbound Scan Time'].set(self.data_frame.loc[data_index, 'Inbound Scan Time'])
            self.param_dict['Inbound status'].set(self.data_frame.loc[data_index, 'Inbound status'])
            self.param_dict['Pickup Date 减 Scheduled Delivery Date'].set(
                self.data_frame.loc[data_index, 'Pickup Date 减 Scheduled Delivery Date'])
            self.param_dict['Pickup Date'].set(self.data_frame.loc[data_index, 'Pickup Date'])
            self.param_dict['Pickup Time'].set(self.data_frame.loc[data_index, 'Pickup Time'])
            self.param_dict['Pickup Status'].set(self.data_frame.loc[data_index, 'Pickup Status'])
            self.param_dict['Drop off date 减 Pickup Date'].set(
                self.data_frame.loc[data_index, 'Drop off date 减 Pickup Date'])
            self.param_dict['Drop off date'].set(self.data_frame.loc[data_index, 'Drop off date'])
            self.param_dict['Drop off time'].set(self.data_frame.loc[data_index, 'Drop off time'])
            self.param_dict['Drop off remark'].set(self.data_frame.loc[data_index, 'Drop off remark'])

            self.temp_window.insert('', 0, f'item{self.index}', values=(
                self.param_dict['Reason for Complaint'].get(),
                self.param_dict['Details of Complaint'].get(),
                self.param_dict['Tracking Code'].get(),
                self.param_dict['Drop off status'].get(),
                self.param_dict['Earliest Dropoff Time'].get(),
                self.param_dict['Latest Dropoff Time'].get(),
                self.param_dict['Scheduled Delivery Date'].get(),
                self.param_dict['Shipment status'].get(),
                self.param_dict['Inbound Scan Date 减 Scheduled Delivery Date'].get(),
                self.param_dict['Inbound Scan Date (Linehaul)'].get(),
                self.param_dict['Inbound Scan Time'].get(),
                self.param_dict['Inbound status'].get(),
                self.param_dict['Pickup Date 减 Scheduled Delivery Date'].get(),
                self.param_dict['Pickup Date'].get(),
                self.param_dict['Pickup Time'].get(),
                self.param_dict['Pickup Status'].get(),
                self.param_dict['Drop off date 减 Pickup Date'].get(),
                self.param_dict['Drop off date'].get(),
                self.param_dict['Drop off time'].get(),
                self.param_dict['Drop off remark'].get()
            ))
            self.temp_window.pack(pady=20)
            print(self.param_dict['Tracking Code'].get())

        elif self.day == '3':
            self.param_dict['Tracking Code'].set(self.data_frame.loc[data_index, 'Tracking Code'])
            self.param_dict['Drop off status'].set(self.data_frame.loc[data_index, 'Drop off status'])
            self.param_dict['Scheduled Delivery Date'].set(self.data_frame.loc[data_index, 'Scheduled Delivery Date'])
            self.param_dict['Earliest Dropoff Time'].set(self.data_frame.loc[data_index, 'Earliest Dropoff Time'])
            self.param_dict['Latest Dropoff Time'].set(self.data_frame.loc[data_index, 'Latest Dropoff Time'])
            self.param_dict['Shipment status'].set(self.data_frame.loc[data_index, 'Shipment status'])
            self.param_dict['Inbound Scan Date 减 Scheduled Delivery Date'].set(
                self.data_frame.loc[data_index, 'Inbound Scan Date 减 Scheduled Delivery Date'])
            self.param_dict['Inbound Scan Date (Linehaul)'].set(
                self.data_frame.loc[data_index, 'Inbound Scan Date (Linehaul)'])
            self.param_dict['Inbound Scan Time'].set(self.data_frame.loc[data_index, 'Inbound Scan Time'])
            self.param_dict['Inbound status'].set(self.data_frame.loc[data_index, 'Inbound status'])
            self.param_dict['Pickup Date 减 Scheduled Delivery Date'].set(
                self.data_frame.loc[data_index, 'Pickup Date 减 Scheduled Delivery Date'])
            self.param_dict['Pickup Date'].set(self.data_frame.loc[data_index, 'Pickup Date'])
            self.param_dict['Pickup Time'].set(self.data_frame.loc[data_index, 'Pickup Time'])
            self.param_dict['Pickup Status'].set(self.data_frame.loc[data_index, 'Pickup Status'])
            self.param_dict['Drop off date 减 Pickup Date'].set(
                self.data_frame.loc[data_index, 'Drop off date 减 Pickup Date'])
            self.param_dict['Drop off date'].set(self.data_frame.loc[data_index, 'Drop off date'])
            self.param_dict['Drop off Time'].set(self.data_frame.loc[data_index, 'Drop off Time'])
            self.param_dict['Drop off remark'].set(self.data_frame.loc[data_index, 'Drop off remark'])

            self.temp_window.insert('', 0, f'item{self.index}', values=(
                self.param_dict['Tracking Code'].get(),
                self.param_dict['Drop off status'].get(),
                self.param_dict['Scheduled Delivery Date'].get(),
                self.param_dict['Earliest Dropoff Time'].get(),
                self.param_dict['Latest Dropoff Time'].get(),
                self.param_dict['Shipment status'].get(),
                self.param_dict['Inbound Scan Date 减 Scheduled Delivery Date'].get(),
                self.param_dict['Inbound Scan Date (Linehaul)'].get(),
                self.param_dict['Inbound Scan Time'].get(),
                self.param_dict['Inbound status'].get(),
                self.param_dict['Pickup Date 减 Scheduled Delivery Date'].get(),
                self.param_dict['Pickup Date'].get(),
                self.param_dict['Pickup Time'].get(),
                self.param_dict['Pickup Status'].get(),
                self.param_dict['Drop off date 减 Pickup Date'].get(),
                self.param_dict['Drop off date'].get(),
                self.param_dict['Drop off Time'].get(),
                self.param_dict['Drop off remark'].get()
            ))
            self.temp_window.pack(pady=20)
            print(self.param_dict['Tracking Code'].get())

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

    def show_pic(self, event=None):
        # 生成 dict_data
        result_dict = self.get_dict_from_tracking_code(
            tracking_code=self.data_frame.loc[self.index, 'Tracking Code']
        )
        # data_dict = {'size': 15, 'q': self.data_frame.loc[self.index, 'Tracking Code'],
        #              'filters': {}, 'sorts': ['-dropoff_earliest_ts']}
        # json_data = json.dumps(data_dict)

        session = requests.Session()
        # user = 'yanxia.ji'
        # password = 'Axl12345'
        # response = session.post(url=self.url, headers=self.header, data=json_data, auth=HttpNtlmAuth(user, password))
        #
        # result_dict = json.loads(response.text)
        # print(result_dict)

        # 如果存在照片，就显示
        if result_dict['results'][0]['pod']['images'] != []:
            # 如果是单张照片
            if len(result_dict['results'][0]['pod']['images']) == 1:
                img_url = result_dict['results'][0]['pod']['images'][0]['url']
                img_url_response = session.get(img_url)

                # 写入文件到 cache
                with open(f'tools/img_cache/{img_url[-10:]}.png', 'wb') as fp:
                    fp.write(img_url_response.content)

                if 'street2' in result_dict['results'][0]['shipment']['dropoff_address'].keys():
                    address_street2 = result_dict['results'][0]['shipment']['dropoff_address']['street2'] + ' '
                else:
                    address_street2 = "" + ' '
                address_street = result_dict['results'][0]['shipment']['dropoff_address']['street'] + ' '
                address_city = result_dict['results'][0]['shipment']['dropoff_address']['city'] + ' '
                address_state = result_dict['results'][0]['shipment']['dropoff_address']['state'] + ' '
                address_zipcode = result_dict['results'][0]['shipment']['dropoff_address']['zipcode'] + ' '
                address = address_street2 + address_street + address_city + address_state + address_zipcode

                img = cv2.imread(f'tools/img_cache/{img_url[-10:]}.png')
                img = process_image(img)
                cv2.imshow(f"address: {address}", img)
                cv2.waitKey()
            # 多张照片
            if len(result_dict['results'][0]['pod']['images']) > 1:
                imgs = []
                for img_url in result_dict['results'][0]['pod']['images']:
                    img_url_response = session.get(img_url['url'])

                    # 写入文件到 cache
                    with open(f'tools/img_cache/{img_url["url"][-10:]}.png', 'wb') as fp:
                        fp.write(img_url_response.content)
                        imgs.append(f'tools/img_cache/{img_url["url"][-10:]}.png')

                if 'street2' in result_dict['results'][0]['shipment']['dropoff_address'].keys():
                    address_street2 = result_dict['results'][0]['shipment']['dropoff_address']['street2'] + ' '
                else:
                    address_street2 = "" + ' '

                address_street = result_dict['results'][0]['shipment']['dropoff_address']['street'] + ' '
                address_city = result_dict['results'][0]['shipment']['dropoff_address']['city'] + ' '
                address_state = result_dict['results'][0]['shipment']['dropoff_address']['state'] + ' '
                address_zipcode = result_dict['results'][0]['shipment']['dropoff_address']['zipcode'] + ' '
                address = address_street2 + address_street + address_city + address_state + address_zipcode

                # 依次显示照片
                for img in imgs:
                    img = cv2.imread(img)
                    img = process_image(img)
                    cv2.imshow(f"address: {address} have more than one pic", img)
                    cv2.waitKey()
        else:
            if 'street2' in result_dict['results'][0]['shipment']['dropoff_address'].keys():
                address_street2 = result_dict['results'][0]['shipment']['dropoff_address']['street2'] + ' '
            else:
                address_street2 = " "
            address_street = result_dict['results'][0]['shipment']['dropoff_address']['street'] + ' '
            address_city = result_dict['results'][0]['shipment']['dropoff_address']['city'] + ' '
            address_state = result_dict['results'][0]['shipment']['dropoff_address']['state'] + ' '
            address_zipcode = result_dict['results'][0]['shipment']['dropoff_address']['zipcode'] + ' '
            address = address_street2 + address_street + address_city + address_state + address_zipcode

            messagebox.showinfo('没有照片', message=f'地址为: {address}')
            self.window.focus_force()

    def clear_cache(self):
        if not os.path.exists('tools/img_cache'):
            os.mkdir('tools/img_cache')
        del_list = os.listdir('tools/img_cache')
        if len(del_list) == 0:
            messagebox.showinfo(title='清除失败', message='无缓存')
            return
        file_size_sum = 0
        for f in del_list:
            file_path = os.path.join('tools/img_cache', f)
            if os.path.isfile(file_path):
                file_size_sum += self.get_filesize(file_path)
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        messagebox.showinfo(title='清除成功', message=f'清除缓存共 {round(file_size_sum, 1)}mb')

    @staticmethod
    def get_filesize(file_path):
        file_size = os.path.getsize(file_path)
        file_size = file_size / float(1024 * 1024)
        return round(file_size, 2)

    def confirm(self, event=None):
        print(self.answer)
        print(self.answer.get())
        answer_index = self.answer.get()
        print('answer_index', int(answer_index))
        analyser_utils.copy_reason(
            data_frame_row=self.data_frame.iloc[self.index: self.index + 1, :],
            index=int(answer_index)
        )
        messagebox.showinfo(title='确定', message='您的输入已写入')
        self.window.focus_force()

    def hand_in_result(self):
        # 生成 csv
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        path = str(self.save_folder_path) + '/最终版' + date_time + '.csv'

        res_df = self.write_in()

        # 周三的需要改动列名
        if self.day == '3':
            res_df.rename(columns={'AH Assessment': 'HF Reason Code'}, inplace=True)
        # 这里 res_df 中的五列将带 x 的写回去，并 drop 掉
        res_df.to_csv(path, index=False)

        messagebox.showinfo(title='成功', message=f'已生成 {path}')

    def write_in(self):
        def get_index(tracking_code, source_df):
            return source_df[source_df['Tracking Code'] == tracking_code].index

        data_frame = self.data_frame.copy()
        source_df = self.source_df.copy()
        # 把 data_frame 根据相同的 tracking code 将五列写入 source_df 返回 res_df
        for index, row in data_frame.iterrows():
            source_df.loc[get_index(data_frame.loc[index, 'Tracking Code'], source_df),
                          'Issue Category'] = data_frame.loc[index, 'Issue Category']
            source_df.loc[get_index(data_frame.loc[index, 'Tracking Code'], source_df),
                          'Delivery Comments'] = data_frame.loc[index, 'Delivery Comments']
            source_df.loc[get_index(data_frame.loc[index, 'Tracking Code'], source_df),
                          'AH Assessment'] = data_frame.loc[index, 'AH Assessment']
            source_df.loc[get_index(data_frame.loc[index, 'Tracking Code'], source_df),
                          'POD Quality'] = data_frame.loc[index, 'POD Quality']
            source_df.loc[get_index(data_frame.loc[index, 'Tracking Code'], source_df),
                          'POD Valid?'] = data_frame.loc[index, 'POD Valid?']
        return source_df

    @staticmethod
    def open_dictionary():
        os.system(os.getcwd() + '/tools/files/dictionary.xlsx')


def process_image(img):
    min_side = 768
    size = img.shape
    h, w = size[0], size[1]
    # 长边缩放为min_side
    scale = max(w, h) / float(min_side)
    new_w, new_h = int(w / scale), int(h / scale)
    resize_img = cv2.resize(img, (new_w, new_h))
    # 填充至min_side * min_side
    if new_w % 2 != 0 and new_h % 2 == 0:
        top, bottom, left, right = (min_side - new_h) / 2, (min_side - new_h) / 2, (min_side - new_w) / 2 + 1, (
                    min_side - new_w) / 2
    elif new_h % 2 != 0 and new_w % 2 == 0:
        top, bottom, left, right = (min_side - new_h) / 2 + 1, (min_side - new_h) / 2, (min_side - new_w) / 2, (
                    min_side - new_w) / 2
    elif new_h % 2 == 0 and new_w % 2 == 0:
        top, bottom, left, right = (min_side - new_h) / 2, (min_side - new_h) / 2, (min_side - new_w) / 2, (
                    min_side - new_w) / 2
    else:
        top, bottom, left, right = (min_side - new_h) / 2 + 1, (min_side - new_h) / 2, (min_side - new_w) / 2 + 1, (
                    min_side - new_w) / 2
    pad_img = cv2.copyMakeBorder(resize_img, int(top), int(bottom), int(left), int(right), cv2.BORDER_CONSTANT,
                                 value=[0, 0, 0])  # 从图像边界向上,下,左,右扩的像素数目
    return pad_img


class Thursday(object):
    def __init__(self, init_df, policy):
        self.init_df = init_df
        self.policy = policy

    def analyse(self):
        res_data = self.init_df.copy()
        result = pd.DataFrame(columns=res_data.columns)
        for index, row in self.init_df.iterrows():
            # 修改 Scheduled Delivery Date 成为 %Y-%m-%d
            temp = analyser_utils.change_Scheduled_Delivery_Date(res_data.iloc[index: index + 1, :])
            # 填入 week √
            temp = analyser_utils.get_week_num(temp)
            # 修改时区
            # temp = analyser_utils.data_frame_row_time_change(temp)
            res_data.iloc[index: index + 1, :] = analyser_utils.get_status(temp, day='4', policy=self.policy)
            result = pd.concat([result, temp])
        result['Updated Reason Code'] = result['AH Assessment']
        return result


class Wednesday(object):
    def __init__(self, init_df, policy):
        self.init_df = init_df
        self.policy = policy

    def analyse(self):
        res_data = self.init_df.copy()
        res_data.rename(columns={'HF Reason Code': 'AH Assessment', 'POD Qaulity': 'POD Quality'}, inplace=True)
        result = pd.DataFrame(columns=res_data.columns)
        for index, row in self.init_df.iterrows():
            # 修改 Scheduled Delivery Date 成为 %Y-%m-%d
            temp = analyser_utils.change_Scheduled_Delivery_Date(res_data.iloc[index: index + 1, :])
            # 填入 week √
            temp = analyser_utils.get_week_num(temp)
            # 修改时区
            # temp = analyser_utils.data_frame_row_time_change(temp)
            # 分析 status
            res_data.iloc[index: index + 1, :] = analyser_utils.get_status(temp, day='3', policy=self.policy)
            result = pd.concat([result, temp])
        result['Updated Reason Code'] = result['AH Assessment']
        return result
