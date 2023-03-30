import os
import zipfile
import pandas as pd
from AxleParsingTools.utils.preprocessing_data import preprocessing_data
from AxleParsingTools.utils.analyser import Wednesday


def save_file(src, dst):
    with open(dst, mode='wb') as fp:
        for chunk in src.chunks():
            fp.write(chunk)


def get_all_report(zip_src, dst_dir='cache/'):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')
        return

    dir_list = os.listdir('cache/all')
    res_df = pd.DataFrame()
    for file in dir_list:
        file_path = 'cache/all' + '/' + file
        temp_df = pd.read_csv(file_path)
        res_df = pd.concat([res_df, temp_df])
    return res_df


def process_all(ending_df, claim_df, all_report_df, policy):
    structured_df = preprocessing_data(
        ending_df=ending_df,
        boss2me_df=claim_df,
        all_report_df=all_report_df,
    )
    structured_df = structured_df.rename(columns={'DELIVERY_DATE': 'Scheduled Delivery Date'})
    # 列名先改一下
    structured_df.rename(columns={'Drop off Time': 'Drop off time'}, inplace=True)

    wednesday = Wednesday(structured_df, policy=policy)
    res_df = wednesday.analyse()

    # 列名先改回来
    res_df.rename(columns={'Drop off time': 'Drop off Time'}, inplace=True)

    # 生成 csv
    try:
        res_df = res_df.drop(columns=['Week#', 'Updated Reason Code'])
    except BaseException:
        pass

    return res_df
