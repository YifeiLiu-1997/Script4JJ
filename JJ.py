"""
    1. 将boss "tracking code" 改为和 report "Tracking Code" 一致
    2. 合并二者，生成新 pd --> same
    3. initialize res_data 为 ending 的所有标题
    4. 将 res_data 的一些标题改为 same 的
    5. 遍历 same 的标题，将 same 的数据写入 same 和 res_data 共有的标题下
    6. 将 res_data 的标题重置为 ending 的标题
    7. 将 res_data 写入 csv 文档并输出
    疯了吧 我靠
    
"""
import pandas as pd
from tkinter import *
from tkinter.filedialog import askopenfilename
import os
import datetime
import re
from utils.analyser import Thursday
from utils.analyser_utils import *

pd.options.display.max_columns = None


def change_title_name(pd, pd_title, pd_title_change):
    print(pd_title, 'change to', pd_title_change)
    pd = pd.rename(columns={pd_title: pd_title_change})
    return pd


def write_into_result(big_sheet_path, boss2me_path, report_path):
    # 0. 获取文件
    big_sheet = pd.read_csv(big_sheet_path, dtype='object')
    boss2me = pd.read_csv(boss2me_path, dtype='object')
    report = pd.read_csv(report_path, dtype='object')

    # 3. initialize res_data
    res_data = pd.DataFrame(columns=big_sheet.columns, dtype='object')

    # 1. 将boss "tracking code" 改为和 report "Tracking Code" 一致
    # boss 的 tracking code 有多种可能 "tracking #" or "Tracking Number"
    boss2me = change_title_name(boss2me, re.search(r'\'[Tt]racking(#| Number| code| Code|_code|_Code)\'',
                                                   str(boss2me.columns)).group(0)[1:-1], "Tracking Code")

    # 2. 合并 boss 和 report 合并为 same
    same = pd.merge(boss2me, report, how='left', on='Tracking Code')

    # 4. 将 res_data 的一些标题改为 same 的
    # ending 与 same 的不同除 Region Code --> Region, REgion Code --> Region
    # ending_wednesday 的 Drop off Time ending_thursday是 Drop off time --> Dropoff Time
    res_data = change_title_name(res_data, re.search(r'\'[Tt]racking(#| Number| code| Code)\'',
                                                   str(res_data.columns)).group(0)[1:-1], "Tracking Code")
    res_data = change_title_name(res_data, re.search(r'\'((Region Code)|(REgion Code)|(region Code)|(rEgion Code)|(Region code)|(REgion code))\'',
                                                     str(res_data.columns)).group(0)[1:-1], "Region")
    res_data = change_title_name(res_data, 'Assignment ID', 'Assignment Id')
    res_data = change_title_name(res_data, re.search(r'\'(Issue)|(Reason for Complaint)\'', str(res_data.columns)).group(0)[:-1], 'Reason for Complaint')
    res_data = change_title_name(res_data, 'Inbound Scan Date (Linehaul)', 'Inbound Scan Date')
    res_data = change_title_name(res_data, 'Pickup remark', 'Pickup Remark')
    res_data = change_title_name(res_data, 'Drop off date', 'Dropoff Date')
    res_data = change_title_name(res_data, re.search(r'\'Drop off [Tt]ime\'',
                                                     str(res_data.columns)).group(0)[1:-1], "Dropoff Time")
    res_data = change_title_name(res_data, 'Drop off status', 'Dropoff Status')
    res_data = change_title_name(res_data, 'Drop off remark', 'Dropoff Remark')
    res_data = change_title_name(res_data, 'Requested Amount', 'Requested Credit Amount')

    # 解决 Reason for complaint 问题
    if 'Issue' in same.columns:
        res_data['Reason for Complaint'] = same['Issue']

    # 5. 遍历 same 的标题，将 same 的数据写入 same 和 res_data 共有的标题下
    print('\nres', res_data.columns)
    for title in same.columns:
        if title in res_data.columns:
            res_data[title] = same[title]
            print(title + ' success to write in')

    # 6. 将 res_data 的标题重置为 ending 的标题
    res_data.columns = big_sheet.columns

    # 7. 保存到桌面
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # 8. 更改 res_data 的逻辑
    if 'thursday' in big_sheet_path:
        thursday = Thursday(res_data)
        res_data = thursday.analyse()
    if 'wednesday' in big_sheet_path:
        pass

    res_data.to_csv(os.path.join(os.path.expanduser("~"), 'Desktop') +
                    '\{}.csv'.format(str(stamp)), index=False)


def select_path_1():
    path_ = askopenfilename()
    path_1.set(path_)
    return path_


def select_path_2():
    path_ = askopenfilename()
    path_2.set(path_)
    return path_


def select_path_3():
    path_ = askopenfilename()
    path_3.set(path_)
    return path_


def auto_run():
    e_path = path_1.get().replace('/', '//')
    b_path = path_2.get().replace('/', '//')
    a_path = path_3.get().replace('/', '//')
    write_into_result(e_path, b_path, a_path)


if __name__ == '__main__':
    window = Tk()
    window.title('姬姬专用')
    window.geometry('850x400')
    path_1 = StringVar()
    path_2 = StringVar()
    path_3 = StringVar()

    # label ending
    Label(window, text="ending file:").place(x=100, y=100)
    ending_path = Entry(window, textvariable=path_1, width='60').place(x=220, y=100)
    button_1 = Button(window, text="select", command=select_path_1, width='10').place(x=680, y=100)

    # label boss2me
    Label(window, text="boss2me file:").place(x=100, y=150)
    boss2me_path = Entry(window, textvariable=path_2, width='60').place(x=220, y=150)
    button_2 = Button(window, text="select", command=select_path_2, width='10').place(x=680, y=150)

    # label all_download
    Label(window, text="all report file:").place(x=100, y=200)
    all_download_path = Entry(window, textvariable=path_3, width='60').place(x=220, y=200)
    button_3 = Button(window, text="select", command=select_path_3, width='10').place(x=680, y=200)

    # label what_you_want
    Label(window, text="generate path:").place(x=100, y=250)

    # button
    button_result = Button(window, text='generate', width='10', command=auto_run).place(x=680, y=250)

    window.mainloop()
