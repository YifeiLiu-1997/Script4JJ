import pandas as pd
import os

from tkinter import Toplevel, StringVar, Label, Button, Entry, messagebox
from tkinter.filedialog import askdirectory


def update_2024_5_31(func):
    def wrapper(*args, **kwargs):
        # 修改之前的 res_df
        res_df, folder_path = func(*args, **kwargs)

        # all 的 df 中 Region 是 SMF 的都改成 SFO
        res_df['Region'] = res_df['Region'].replace('SMF', 'SFO')

        # 保存 all
        res_df.to_csv(folder_path.get() + '/all.csv', index=False)
        path = folder_path.get() + '/all.csv'
        messagebox.showinfo(title='成功', message=f'输出路径为: {path}')
        return res_df

    return wrapper


class Concat(object):
    def __init__(self, root):
        self.root = root

    def get_folder_path(self):
        folder_path = askdirectory()
        self.folder_path.set(folder_path)

    @update_2024_5_31
    def concat_from_folder(self):
        dir_list = os.listdir(self.folder_path.get())
        res_df = pd.DataFrame()
        for file in dir_list:
            file_path = self.folder_path.get() + '/' + file
            temp_df = pd.read_csv(file_path)
            res_df = pd.concat([res_df, temp_df])
        return res_df, self.folder_path

    def run(self):
        self.window = Toplevel(master=self.root)
        self.window.geometry('1000x120')
        self.folder_path = StringVar()

        # label ending
        Label(self.window, text="要合并的文件夹:").place(x=100, y=50)
        Entry(self.window, textvariable=self.folder_path, width='60').place(x=220, y=50)
        Button(self.window, text="选择文件夹", command=self.get_folder_path, width='10').place(x=680, y=50)

        # button
        Button(self.window, text='生成', width='10', command=self.concat_from_folder).place(x=780, y=50)
        print(self.window.focus)
        self.window.mainloop()
