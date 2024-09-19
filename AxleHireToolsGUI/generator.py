"""
    填完数字之后，传回来加数字的 csv，点击生成，出结果
"""
import warnings
import pandas as pd
import datetime

from utils.analyser import Wednesday, Thursday
from tkinter import Toplevel

warnings.filterwarnings('ignore')


class Generator(object):
    def __init__(self, root=None):
        self.root = root
        self.window = Toplevel(master=self.root)
        self.reason_code = pd.read_csv('utils/files/JJ - Reason code.csv')

    def options(self):
        pass

    def get_first_by_already_vlookup_files(self, already_file_path, policy, save_path):
        # 列名先改一下
        already_df = pd.read_csv(already_file_path)
        already_df.rename(
            columns={'Drop off Time': 'Drop off time', 'Earliest Dropoff Date': 'Scheduled Delivery Date'},
            inplace=True)

        wednesday = Wednesday(already_df, policy=policy)
        result_df = wednesday.analyse()

        # 列名先改回来
        result_df.rename(columns={'Drop off time': 'Drop off Time', 'Scheduled Delivery Date': 'Earliest Dropoff Date'},
                         inplace=True)

        # 生成 csv
        res_df = result_df.copy()
        try:
            res_df = res_df.drop(columns=['Week#', 'Updated Reason Code'])
        except BaseException:
            pass
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        res_df.to_csv(str(save_path) + '/HF first' + date_time + '.csv', index=False)

    def get_final(self, csv_file):
        # 1. 读入传入的 csv
        res_df = pd.read_csv(csv_file)
        res_df.rename(columns={'HF Reason Code': 'AH Assessment'}, inplace=True)
        # 2. 遍历 res_df
        for idx, row in res_df.iterrows():
            res_df.iloc[idx: idx + 1, :] = self.parse_rows(res_df.iloc[idx: idx + 1, :])
            print(f'\rwrite {idx} rows', end='')
        return res_df

    def parse_rows(self, data_frame_rows):
        # 解析每一行
        if pd.isna(data_frame_rows['Answer Number'].values[0]):
            return data_frame_rows

        number = int(data_frame_rows['Answer Number'].values[0]) if not isinstance(
            data_frame_rows['Answer Number'].values[0], str) else data_frame_rows['Answer Number'].values[0]
        # print(type(number))
        # 不是数字，一定是 14 15 apt 这种形式
        if not str(number).isnumeric():
            answer_list = str(number).split(' ')
            # 三种形式 pic shows building #,the correct is #
            if 'apt' in answer_list:
                data_frame_rows = self.copy_rows(data_frame_rows, int(109))
                apt_answer = str(data_frame_rows['POD Quality'].values[0]). \
                    replace('shows apt #', f'shows apt #{answer_list[0]}'). \
                    replace('the correct is apt#', f'the correct is apt#{answer_list[1]}')
                data_frame_rows['POD Quality'] = [apt_answer]
                return data_frame_rows
            elif 'st' in answer_list:
                data_frame_rows = self.copy_rows(data_frame_rows, int(108))
                s_answer = str(data_frame_rows['POD Quality'].values[0]). \
                    replace('shows street #', f'shows street #{answer_list[0]}'). \
                    replace('the correct is #', f'the correct is #{answer_list[1]}')
                data_frame_rows['POD Quality'] = [s_answer]
                return data_frame_rows
            elif 'b' in answer_list:
                data_frame_rows = self.copy_rows(data_frame_rows, int(107))
                b_answer = str(data_frame_rows['POD Quality'].values[0]). \
                    replace('shows building #', f'shows building #{answer_list[0]}'). \
                    replace('the correct is #', f'the correct is #{answer_list[1]}')
                data_frame_rows['POD Quality'] = [b_answer]
                return data_frame_rows
            else:
                return data_frame_rows
        else:
            data_frame_rows = self.copy_rows(data_frame_rows, int(number))
            return data_frame_rows

    def copy_rows(self, data_frame_row, index):
        pd.set_option("display.max_columns", 50)

        def nan_to_none(x):
            if str(x) == 'nan' or pd.isna(x):
                return ''
            return x

        if pd.isna(data_frame_row['POD Valid?'].values[0]) and pd.isna(data_frame_row['POD Quality'].values[0]) and \
                pd.isna(data_frame_row['Issue Category'].values[0]) and pd.isna(
            data_frame_row['Delivery Comments'].values[0]) and \
                pd.isna(data_frame_row['AH Assessment'].values[0]):
            data_frame_row['POD Valid?'] = [nan_to_none(self.reason_code.loc[index, 'POD'])]
            data_frame_row['POD Quality'] = [nan_to_none(self.reason_code.loc[index, 'POD Qaulity'])]
            data_frame_row['Issue Category'] = [self.reason_code.loc[index, 'Issue Category']]
            data_frame_row['Delivery Comments'] = [self.reason_code.loc[index, 'Delivery Comments']]

            if data_frame_row['Delivery Comments'].values == ['Delivery Cannot Be Confirmed']:
                data_frame_row['Delivery Comments'] = ['POD quality issue']

            data_frame_row['AH Assessment'] = [self.reason_code.loc[index, 'AH Assignment']]

            return data_frame_row

        # 如果不是空的，加一个 / 再将内容附着上
        else:
            data_frame_row['POD Valid?'] = [nan_to_none(self.reason_code.loc[index, 'POD'])]
            data_frame_row['POD Quality'] = [nan_to_none(self.reason_code.loc[index, 'POD Qaulity'])]
            if index == 122 or index == 123:
                return data_frame_row
            # 如果本来就有，比如已经是 Delivery 了，你再加个 Delivery 就不对了
            if self.reason_code.loc[index, 'Issue Category'] in str(data_frame_row['Issue Category'].values[0]):
                pass
            else:
                data_frame_row['Issue Category'] = [
                    str(data_frame_row['Issue Category'].values[0]) + '/' + self.reason_code.loc[
                        index, 'Issue Category']]
            data_frame_row['Delivery Comments'] = [
                str(data_frame_row['Delivery Comments'].values[0]) + '/' + self.reason_code.loc[
                    index, 'Delivery Comments']]
            data_frame_row['AH Assessment'] = [
                str(data_frame_row['AH Assessment'].values[0]) + '/' + self.reason_code.loc[index, 'AH Assignment']]
            return data_frame_row


if __name__ == '__main__':
    g = Generator()
    g.get_final(csv_file=r"D:\Files\work\2023-3-29 HF\DG.csv"). \
        to_csv(r"D:\Files\work\2023-3-29 HF\ZL.csv", index=False)
    # g.get_first_by_already_vlookup_files(
    #     already_file_path=r"D:\Files\work\2023-3-1 HF\F75.csv",
    #     policy=30,
    #     save_path=r"D:\Files\work\2023-3-1 HF"
    # )
