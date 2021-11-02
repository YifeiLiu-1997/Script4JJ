import datetime
import pandas as pd
import re

DICT_DF = pd.read_excel('utils/files/dictionary.xlsx')


def is_mouth_day_year(date):
    try:
        datetime.datetime.strptime(date, "%m/%d/%Y")
        return True
    except:
        return False


def get_week_num(data_frame_row):
    date_str = data_frame_row['Scheduled Delivery Date'].values[0]
    # 如果 scheduled date 是月日年
    if is_mouth_day_year(date_str):
        res_date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
        data_frame_row['Week#'] = [res_date.isocalendar()[1]]
        return data_frame_row
    else:
        res_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        data_frame_row['Week#'] = [res_date.isocalendar()[1]]
        return data_frame_row


def copy_reason(data_frame_row, index):
    copy_df = DICT_DF[DICT_DF.index == index]
    data_frame_row['Issue Category'] = copy_df['Issue Category'].values
    data_frame_row['Delivery Comments'] = copy_df['Delivery Comments'].values
    data_frame_row['AH Assessment'] = copy_df['AH Assessment'].values
    return data_frame_row


def get_shipment_status(data_frame_row):
    if data_frame_row['Shipment status'].values[0] == 'GEOCODED':
        # TODO: 复制
        data_frame_row = copy_reason(data_frame_row, 29)
        return data_frame_row
    return data_frame_row


def get_drop_off_status(data_frame_row):
    if data_frame_row['Drop off status'].values[0] == 'DISCARDED':
        # cancel
        if "Cancel".lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 20)
            return data_frame_row
        # damaged
        if "Damaged".lower() in data_frame_row['Drop off remark'].values[0].lower():
            if "outbound".lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 5)
                return data_frame_row
            if "inbound".lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 26)
                return data_frame_row
            if "RECEIVED_DAMAGED".lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 26)
                return data_frame_row
        # missing
        if "Missing".lower() in data_frame_row['Drop off remark'].values[0].lower():
            if "outbound".lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 4)
                return data_frame_row
            if "inbound".lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 25)
                return data_frame_row
        # discard
        if "Discard".lower() in data_frame_row['Drop off remark'].values[0].lower():
            if data_frame_row['Pickup Status'].values[0] == 'FAILED':
                data_frame_row = copy_reason(data_frame_row, 3)
                return data_frame_row
            if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
                data_frame_row = copy_reason(data_frame_row, 52)
                return data_frame_row
        # None
        if data_frame_row['Drop off remark'].values[0] is None:
            data_frame_row = copy_reason(data_frame_row, 52)
            return data_frame_row

    if data_frame_row['Drop off status'].values[0] is None:
        if data_frame_row['Inbound status'].values[0] == 'MISSING':
            data_frame_row = copy_reason(data_frame_row, 25)
            return data_frame_row
        else:
            if data_frame_row['Pickup Status'].values[0] == 'MISSING':
                data_frame_row = copy_reason(data_frame_row, 4)
                return data_frame_row

    if data_frame_row['Drop off status'].values[0] == 'EN_ROUTE':
        if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
            data_frame_row = copy_reason(data_frame_row, 52)
            return data_frame_row
        if data_frame_row['Pickup Status'].values[0] == 'FAILED':
            data_frame_row = copy_reason(data_frame_row, 3)
            return data_frame_row

    if data_frame_row['Drop off status'].values[0] == 'PENDING':
        if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
            data_frame_row = copy_reason(data_frame_row, 52)
            return data_frame_row
        if data_frame_row['Pickup Status'].values[0] == 'FAILED':
            data_frame_row = copy_reason(data_frame_row, 3)
            return data_frame_row

    if data_frame_row['Drop off status'].values[0] == 'FAILED':
        if data_frame_row['Drop off remark'].values[0] is None:
            data_frame_row = copy_reason(data_frame_row, 52)
            return data_frame_row
        if 'out of cold chain'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 46)
            return data_frame_row
        if 'missing'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 54)
            return data_frame_row
        if 'damaged'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 46)
            return data_frame_row
        if 'wrong'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 14)
            return data_frame_row
        if 'access'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 14)
            return data_frame_row
        if 'answer'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 14)
            return data_frame_row
        if 'can\'t be reach'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 13)
            return data_frame_row
        if 'gates closed'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 14)
            return data_frame_row
        if 'road closed'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 14)
            return data_frame_row
        if 'requested redelivery'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 23)
            return data_frame_row
        if 'redelivery requested'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            data_frame_row = copy_reason(data_frame_row, 23)
            return data_frame_row

    if data_frame_row['Drop off status'].values[0] == 'SUCCEEDED':
        inbound_diff = date_subtract(data_frame_row['Inbound Scan Date (Linehaul)'].values[0],
                                      data_frame_row['Scheduled Delivery Date'].values[0])
        if inbound_diff >= 0:
            if inbound_diff == 0:
                if time_upper_than(data_frame_row['Inbound Scan Time'].values[0], '05:00'):
                    data_frame_row['Inbound Comments'] = ['Inbound late']
                    data_frame_row = copy_reason(data_frame_row, 24)
                    return data_frame_row
            if inbound_diff > 0:
                # 继续判断 pickup
                pickup_diff = date_subtract(data_frame_row['Pickup Date'].values[0],
                                            data_frame_row['Scheduled Delivery Date'].values[0])
                if pickup_diff >= 0:
                    if pickup_diff == 0:
                        if time_upper_than(data_frame_row['Pickup Time'].values[0], '12:00'):
                            print('Pickup Time', data_frame_row['Pickup Time'].values[0])
                            data_frame_row['Pickup Comments'] = ['Pickup after 12pm']
                    else:
                        data_frame_row = copy_reason(data_frame_row, 2)
                        data_frame_row['Pickup Comments'] = [f'outbound late for {pickup_diff} day']
                    data_frame_row['Inbound Comments'] = ['Inbound late']
                    data_frame_row = copy_reason(data_frame_row, 24)
                    return data_frame_row
        else:
            pickup_diff = date_subtract(data_frame_row['Pickup Date'].values[0],
                                        data_frame_row['Scheduled Delivery Date'].values[0])
            if pickup_diff >= 0:
                if pickup_diff == 0:
                    if time_upper_than(data_frame_row['Pickup Time'].values[0], '12:00'):
                        print('Pickup Time', data_frame_row['Pickup Time'].values[0])
                        data_frame_row['Pickup Comments'] = ['Pickup after 12pm']
                else:
                    data_frame_row = copy_reason(data_frame_row, 2)
                    data_frame_row['Delivery Comments'] = [f'Inbound ontime but outbound late for {pickup_diff} day']
                    data_frame_row['Inbound Comments'] = [f'Inbound ontime but outbound late for {pickup_diff} day']

    return data_frame_row


def date_subtract(compared_date, schedule_date):
    compared_date = datetime.datetime.strptime(compared_date, '%Y-%m-%d')
    # 如果 scheduled date 是月日年
    if is_mouth_day_year(schedule_date):
        schedule_date = datetime.datetime.strptime(schedule_date, '%m/%d/%Y')
    else:
        schedule_date = datetime.datetime.strptime(schedule_date, '%Y-%m-%d')
    # print(compared_date)
    # print(schedule_date)
    return (compared_date - schedule_date).days


def time_upper_than(time_str, upper):
    upper_time = datetime.datetime.strptime(upper, '%H:%M')
    time_str = datetime.datetime.strptime(time_str, '%H:%M')
    print(upper_time, '-', time_str, '=', end=' ')
    print(int(upper_time.strftime('%H%M')) - int(time_str.strftime('%H%M')))
    if (int(upper_time.strftime('%H%M')) - int(time_str.strftime('%H%M'))) > 0:
        return False
    else:
        return True

if __name__ == '__main__':
    df = pd.read_csv('files/20211027-152332.csv')
    time_1 = df.loc[3, 'Pickup Time']
    upper = '12:00'
    time_upper_than(time_1, upper)