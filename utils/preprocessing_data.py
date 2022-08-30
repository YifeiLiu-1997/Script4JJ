import re
import pandas as pd


def preprocessing_data(ending_df, boss2me_df, all_report_df, day):
    if day == '4':
        # 0. 获取文件
        big_sheet = ending_df
        boss2me = boss2me_df
        report = all_report_df

        # 3. initialize res_data
        columns_list = list(big_sheet.columns)
        columns_list.append('Earliest Dropoff Date')
        columns_list.append('Latest Dropoff Date')
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
        for title in same.columns:
            if title in res_data.columns:
                res_data[title] = same[title]

        # 6. 将 res_data 的标题重置为 ending 的标题
        res_data.columns = big_sheet.columns

        return res_data

    elif day == '3':
        # 0. 获取文件
        big_sheet = ending_df
        boss2me = boss2me_df
        report = all_report_df

        # 3. initialize res_data
        columns_list = list(big_sheet.columns)
        columns_list.append('delivery_date')
        columns_list.append('Earliest Dropoff Time')
        columns_list.append('Latest Dropoff Time')
        columns_list.append('Earliest Dropoff Date')
        columns_list.append('Latest Dropoff Date')
        res_data = pd.DataFrame(columns=columns_list, dtype='object')

        # 1. 将boss "tracking code" 改为和 report "Tracking Code" 一致
        # boss 的 tracking code 有多种可能 "tracking #" or "Tracking Number"
        boss2me = change_title_name(boss2me, re.search(r'\'[Tt]racking(#| Number| code| Code|_code|_Code|)\'',
                                                       str(boss2me.columns)).group(0)[1:-1], "Tracking Code")

        # 2. 合并 boss 和 report 合并为 same
        same = pd.merge(boss2me, report, how='left', on='Tracking Code')

        # 4. 将 res_data 的一些标题改为 same 的
        # ending 与 same 的不同除 Region Code --> Region, REgion Code --> Region
        # ending_wednesday 的 Drop off Time ending_thursday是 Drop off time --> Dropoff Time
        res_data = change_title_name(res_data, re.search(r'\'[Tt]racking(#| Number| code| Code)\'',
                                                         str(res_data.columns)).group(0)[1:-1], "Tracking Code")
        res_data = change_title_name(res_data, re.search(
            r'\'((Region Code)|(REgion Code)|(region Code)|(rEgion Code)|(Region code)|(REgion code))\'',
            str(res_data.columns)).group(0)[1:-1], "Region")
        res_data = change_title_name(res_data, 'Assignment ID', 'Assignment Id')
        res_data = change_title_name(res_data,
                                     re.search(r'\'(Issue)|(Reason for Complaint)\'', str(res_data.columns)).group(0)[
                                     :-1], 'Reason for Complaint')
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
        for title in same.columns:
            if title in res_data.columns:
                res_data[title] = same[title]

        # 6. 将 res_data 的标题重置为 ending 的标题
        columns_list = list(big_sheet.columns)
        columns_list.append('delivery_date')
        columns_list.append('Earliest Dropoff Time')
        columns_list.append('Latest Dropoff Time')
        columns_list.append('Earliest Dropoff Date')
        columns_list.append('Latest Dropoff Date')
        res_data.columns = columns_list

        return res_data


def change_title_name(pd, pd_title, pd_title_change):
    df = pd.rename(columns={pd_title: pd_title_change})
    return df
