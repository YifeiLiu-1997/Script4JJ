import pandas as pd
import os

from tkinter import Toplevel, StringVar, Label, Button, Entry, messagebox
from tkinter.filedialog import askdirectory


class Concat(object):
    def __init__(self, root):
        self.root = root

    def get_folder_path(self):
        folder_path = askdirectory()
        self.folder_path.set(folder_path)

    def concat_from_folder(self):
        dir_list = os.listdir(self.folder_path.get())
        res_df = pd.DataFrame()
        for file in dir_list:
            file_path = self.folder_path.get() + '/' + file
            temp_df = pd.read_csv(file_path)
            res_df = pd.concat([res_df, temp_df])
        res_df.to_csv(self.folder_path.get() + '/all.csv', index=False)
        path = self.folder_path.get() + '/all.csv'
        messagebox.showinfo(title='成功', message=f'输出路径为: {path}')
        return res_df

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
