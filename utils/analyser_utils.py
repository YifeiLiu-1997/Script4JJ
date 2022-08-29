import os
import datetime
import pandas as pd


DICT_DF = pd.read_excel(os.getcwd() + '/utils/files/dictionary.xlsx')


def is_mouth_day_year(date):
    try:
        datetime.datetime.strptime(date, "%m/%d/%Y")
        return True
    except:
        return False


def get_week_num(data_frame_row):
    date_str = data_frame_row['Scheduled Delivery Date'].values[0]
    if pd.isna(date_str):

        return data_frame_row
    # 如果 scheduled date 是月日年
    if is_mouth_day_year(date_str):
        res_date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
        data_frame_row['Week#'] = [res_date.isocalendar()[1]]
        return data_frame_row
    else:
        res_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        # res_date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        data_frame_row['Week#'] = [res_date.isocalendar()[1]]
        return data_frame_row



def nan_to_none(x):
    if str(x) == 'nan' or pd.isna(x):
        return ''
    return x


def copy_reason(data_frame_row, index):
    # print('values', data_frame_row['POD Valid?'].values[0])
    # print('values', data_frame_row['Issue Category'].values[0])
    copy_df = DICT_DF[DICT_DF.index == index]
    # 如果全是空的，直接复制
    if pd.isna(data_frame_row['POD Valid?'].values[0]) and pd.isna(data_frame_row['POD Quality'].values[0]) and \
        pd.isna(data_frame_row['Issue Category'].values[0]) and pd.isna(data_frame_row['Delivery Comments'].values[0]) and \
        pd.isna(data_frame_row['AH Assessment'].values[0]):
        # print('全是空的')
        data_frame_row['POD Valid?'] = [nan_to_none(copy_df['POD Valid?'].values[0])]
        data_frame_row['POD Quality'] = [nan_to_none(copy_df['POD Quality'].values[0])]
        data_frame_row['Issue Category'] = copy_df['Issue Category'].values
        data_frame_row['Delivery Comments'] = copy_df['Delivery Comments'].values
        data_frame_row['AH Assessment'] = copy_df['AH Assessment'].values
        # print('写进去了')
        return data_frame_row
    # 如果不是空的，加一个 / 再将内容附着上
    else:
        # print('不是空的')
        data_frame_row['POD Valid?'] = [nan_to_none(str(copy_df['POD Valid?'].values[0]))]
        data_frame_row['POD Quality'] = [nan_to_none(str(copy_df['POD Quality'].values[0]))]
        data_frame_row['Issue Category'] = [str(data_frame_row['Issue Category'].values[0]) + '/' + str(copy_df['Issue Category'].values[0])]
        data_frame_row['Delivery Comments'] = [str(data_frame_row['Delivery Comments'].values[0]) + '/' + str(copy_df['Delivery Comments'].values[0])]
        data_frame_row['AH Assessment'] = [str(data_frame_row['AH Assessment'].values[0]) + '/' + str(copy_df['AH Assessment'].values[0])]
        # print('附着进去了')
        return data_frame_row


def get_pickup_and_delivery_status(data_frame_row, day, policy):
    pickup_diff = date_subtract(data_frame_row['Pickup Date'].values[0],
                                data_frame_row['Scheduled Delivery Date'].values[0])

    # 如果 pick 当天送达
    if pickup_diff == 0:
        # 如果 pick 当天晚于 12
        if time_upper_than(data_frame_row['Pickup Time'].values[0], '12:00', 0):
            # print('Pickup Time', data_frame_row['Pickup Time'].values[0])
            data_frame_row['Pickup Comments'] = ['Pickup after 12pm']

            delivery_diff = date_subtract(data_frame_row['Drop off date'].values[0],
                                          data_frame_row['Pickup Date'].values[0])
            # 判断 delivery 当天
            if delivery_diff == 0:
                if time_upper_than(data_frame_row['Drop off time'].values[0],
                                   data_frame_row['Latest Dropoff Time'].values[0], policy):
                    data_frame_row = copy_reason(data_frame_row, 118)
                    return data_frame_row
            # 配送晚于 2 天
            else:
                data_frame_row = copy_reason(data_frame_row, 119)

                if delivery_diff == 1:
                    return data_frame_row
                else:
                    if delivery_diff < 2:
                        return data_frame_row
                    else:
                        # data_frame_row['Delivery Comments'] = [
                        #     f'pickup ok but delivery late for {delivery_diff} days']
                        data_frame_row = write_in_delivery_comments(data_frame_row,
                                                                    f'pickup ok but delivery late for {delivery_diff} days')
                        return data_frame_row
        # 如果 pick 早于 12 点
        else:
            delivery_diff = date_subtract(data_frame_row['Drop off date'].values[0],
                                          data_frame_row['Pickup Date'].values[0])
            # 判断 delivery 当天
            if delivery_diff == 0:
                if time_upper_than(data_frame_row['Drop off time'].values[0],
                                   data_frame_row['Latest Dropoff Time'].values[0], policy):
                    data_frame_row = copy_reason(data_frame_row, 118)
                    return data_frame_row
            # 配送晚于 2 天
            else:
                data_frame_row = copy_reason(data_frame_row, 119)

                if delivery_diff == 1:
                    return data_frame_row
                else:
                    if delivery_diff < 2:
                        return data_frame_row
                    else:
                        # data_frame_row['Delivery Comments'] = [
                        #     f'pickup ok but delivery late for {delivery_diff} days']
                        data_frame_row = write_in_delivery_comments(data_frame_row,
                                                                    f'pickup ok but delivery late for {delivery_diff} days')
                        return data_frame_row
        return data_frame_row

    # 如果 pick 晚了 n 天
    if pickup_diff > 1:
        # 对于周三
        if day == '3':
            data_frame_row = copy_reason(data_frame_row, 41)
            if pickup_diff == 1:
                # data_frame_row['Delivery Comments'] = [
                #     f'Inbound ontime but outbound late for 1 day']
                data_frame_row = write_in_delivery_comments(data_frame_row,
                                                            f'Inbound ontime but outbound late for 1 day')
                data_frame_row['Pickup Comments'] = [
                    f'Inbound ontime but outbound late for 1 day']

                delivery_diff = date_subtract(data_frame_row['Drop off date'].values[0],
                                              data_frame_row['Pickup Date'].values[0])
                # pickup 晚了一天，delivery 当天
                if delivery_diff == 0:
                    # 当天晚了
                    if time_upper_than(data_frame_row['Drop off time'].values[0],
                                       data_frame_row['Latest Dropoff Time'].values[0], policy):
                        data_frame_row = copy_reason(data_frame_row, 118)

                        data_frame_row = write_in_delivery_comments(data_frame_row,
                                                                    f'pickup late for {pickup_diff} day and  delivery late for same day')

                        return data_frame_row
                # pickup 一天， delivery 多天
                else:
                    data_frame_row = copy_reason(data_frame_row, 119)
                    if delivery_diff == 1:
                        data_frame_row = write_in_delivery_comments(data_frame_row,
                                                                    f'pickup late for 1 day and delivery late for 1 day')
                        return data_frame_row
                    else:
                        data_frame_row = write_in_delivery_comments(data_frame_row,
                                                                    f'pickup late for 1 day and delivery late for {delivery_diff} days')
                        return data_frame_row
                return data_frame_row

            # pick up 晚于 1 天，看 delivery
            elif pickup_diff > 1:
                # data_frame_row['Delivery Comments'] = [
                #     f'Inbound ontime but outbound late for {pickup_diff} days']
                data_frame_row = write_in_delivery_comments(data_frame_row,
                                                            f'Inbound ontime but outbound late for {pickup_diff} days')
                data_frame_row['Pickup Comments'] = [
                    f'Inbound ontime but outbound late for {pickup_diff} days']
                return data_frame_row
            return data_frame_row

        # 周四
        if day == '4':
            data_frame_row = copy_reason(data_frame_row, 0)
            if pickup_diff == 1:
                # data_frame_row['Delivery Comments'] = [
                #     f'Inbound ontime but outbound late for 1 day']
                data_frame_row = write_in_delivery_comments(data_frame_row,
                                                            f'Inbound ontime but outbound late for 1 day')
                data_frame_row['Pickup Comments'] = [
                    f'Inbound ontime but outbound late for 1 day']

                delivery_diff = date_subtract(data_frame_row['Drop off date'].values[0],
                                              data_frame_row['Pickup Date'].values[0])
                # pickup 晚了一天，delivery 当天
                if delivery_diff == 0:
                    # 当天晚了
                    if time_upper_than(data_frame_row['Drop off time'].values[0],
                                       data_frame_row['Latest Dropoff Time'].values[0], policy):
                        data_frame_row = copy_reason(data_frame_row, 118)

                        data_frame_row = write_in_delivery_comments(data_frame_row,
                                                                    f'pickup late for {pickup_diff} day and  delivery late for same day')

                        return data_frame_row

                # pickup 一天， delivery 多天
                else:
                    data_frame_row = copy_reason(data_frame_row, 119)
                    if delivery_diff == 1:
                        data_frame_row = write_in_delivery_comments(data_frame_row,
                                                                    f'pickup late for 1 day and delivery late for 1 day')
                        return data_frame_row
                    else:
                        data_frame_row = write_in_delivery_comments(data_frame_row,
                                                                    f'pickup late for 1 day and delivery late for {delivery_diff} days')
                        return data_frame_row
                return data_frame_row

            # pick up 晚于 1 天，看 delivery
            elif pickup_diff > 1:
                # data_frame_row['Delivery Comments'] = [
                #     f'Inbound ontime but outbound late for {pickup_diff} days']
                data_frame_row = write_in_delivery_comments(data_frame_row,
                                                            f'Inbound ontime but outbound late for {pickup_diff} days')
                data_frame_row['Pickup Comments'] = [
                    f'Inbound ontime but outbound late for {pickup_diff} days']
                return data_frame_row
            return data_frame_row

    # pickup 没晚
    else:
        delivery_diff = date_subtract(data_frame_row['Drop off date'].values[0],
                                      data_frame_row['Pickup Date'].values[0])
        if delivery_diff == 0:
            if time_upper_than(data_frame_row['Drop off time'].values[0],
                               data_frame_row['Latest Dropoff Time'].values[0], policy):
                data_frame_row = copy_reason(data_frame_row, 118)
                return data_frame_row
        else:
            data_frame_row = copy_reason(data_frame_row, 119)
            if delivery_diff == 1:
                # data_frame_row['Delivery Comments'] = [
                #     f'pickup ok but delivery late for {delivery_diff} day']
                # data_frame_row = write_in_delivery_comments(data_frame_row,
                #                                             f'pickup ok but delivery late for {delivery_diff} day')
                return data_frame_row
            else:
                if delivery_diff < 2:
                    return data_frame_row
                # data_frame_row['Delivery Comments'] = [
                #     f'pickup ok but delivery late for {delivery_diff} days']
                else:
                    data_frame_row = write_in_delivery_comments(data_frame_row,
                                                            f'pickup ok but delivery late for {delivery_diff} days')
                    return data_frame_row
            return data_frame_row


def get_status(data_frame_row, day, policy):
    # 判断 shipment status 完了
    print(data_frame_row['Shipment status'])
    if 'GEOCODED'.lower() in str(data_frame_row['Shipment status'].values[0]).lower():
        # 这里还要继续分析，但是比较复杂，不过多写了
        data_frame_row = copy_reason(data_frame_row, 29)
        return data_frame_row
    if 'CANCELLED_BEFORE_PICKUP'.lower() in str(data_frame_row['Shipment status'].values[0]).lower():
        data_frame_row = copy_reason(data_frame_row, 20)
        return data_frame_row
    if 'GEOCODE_FAILED'.lower() in str(data_frame_row['Shipment status'].values[0]).lower():
        data_frame_row = copy_reason(data_frame_row, 22)
        return data_frame_row

    # 判断 Inbound status Missing
    if 'MISSING'.lower() in str(data_frame_row['Inbound status'].values[0]).lower():
        data_frame_row = copy_reason(data_frame_row, 25)
        return data_frame_row
    if 'DAMAGED'.lower() in str(data_frame_row['Inbound status'].values[0]).lower():
        data_frame_row = copy_reason(data_frame_row, 26)
        return data_frame_row

    # 开始逐一检查 Drop off status
    if data_frame_row['Drop off status'].values[0] == 'DISCARDED':
        if "Damaged".lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            if day == '4':
                data_frame_row = copy_reason(data_frame_row, 5)
                data_frame_row['Pickup Comments'] = ['Inbound ok but pickup damaged']
                return data_frame_row
            if day == '3':
                data_frame_row = copy_reason(data_frame_row, 34)
                data_frame_row['Pickup Comments'] = ['Inbound ok but pickup damaged']
                return data_frame_row
        if 'RECEIVED_DAMAGED'.lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 26)
            return data_frame_row
        if 'discard'.lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            if day == '3':
                data_frame_row = copy_reason(data_frame_row, 37)
                data_frame_row['Pickup Comments'] = ['Inbound ok but pickup failed']
                return data_frame_row
            if day == '4':
                data_frame_row = copy_reason(data_frame_row, 3)
                data_frame_row['Pickup Comments'] = ['Inbound ok but pickup failed']
                return data_frame_row
        if "Missing".lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            if day == '3':
                data_frame_row = copy_reason(data_frame_row, 35)
                data_frame_row['Pickup Comments'] = ['Inbound ok but pickup failed']
                return data_frame_row
            if day == '4':
                data_frame_row = copy_reason(data_frame_row, 4)
                data_frame_row['Pickup Comments'] = ['Inbound ok but pickup failed']
                return data_frame_row
        if pd.isna(data_frame_row['Drop off remark'].values[0]):
            data_frame_row = copy_reason(data_frame_row, 52)
            return data_frame_row

    if data_frame_row['Drop off status'].values[0] is None:
        if 'missing by inbound' in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 25)
            return data_frame_row
        if 'missing by outbound' in str(data_frame_row['Drop off remark'].values[0]).lower():
            if day == '3':
                data_frame_row = copy_reason(data_frame_row, 35)
                return data_frame_row
            if day == '4':
                data_frame_row = copy_reason(data_frame_row, 4)
                return data_frame_row
        # if data_frame_row['Pickup Status'].values[0] == 'MISSING':
        #     if day == '4':
        #         data_frame_row = copy_reason(data_frame_row, 4)
        #         return data_frame_row
        #     if day == '3':
        #         data_frame_row = copy_reason(data_frame_row, 35)
        #         return data_frame_row

    if data_frame_row['Drop off status'].values[0] == 'EN_ROUTE':
        if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
            data_frame_row = copy_reason(data_frame_row, 52)
            return data_frame_row

    if data_frame_row['Drop off status'].values[0] == 'PENDING':
        if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
            data_frame_row = copy_reason(data_frame_row, 52)
            return data_frame_row
        if data_frame_row['Pickup Status'].values[0] == 'FAILED' or \
                data_frame_row['Pickup Status'].values[0] == 'PENDING':
            if day == '4':
                data_frame_row = copy_reason(data_frame_row, 3)
                return data_frame_row
            elif day == '3':
                data_frame_row = copy_reason(data_frame_row, 31)
                return data_frame_row

    if data_frame_row['Drop off status'].values[0] == 'FAILED':
        # ok
        if pd.isna(data_frame_row['Drop off remark'].values[0]):
            data_frame_row = copy_reason(data_frame_row, 52)
            return data_frame_row
        # 如果 remark 不是空
        if isinstance(data_frame_row['Drop off remark'].values[0], str):
            # ok
            if 'out of cold chain'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 51)
                return data_frame_row
            # ok
            if 'missing'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 52)
                return data_frame_row
            # ok
            if 'damaged'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 46)
                return data_frame_row
            # ok
            # if 'wrong'.lower() in data_frame_row['Drop off remark'].values[0].lower():
            #     data_frame_row = copy_reason(data_frame_row, 14)
            #     return data_frame_row
            # ok
            if 'no access'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 14)
                return data_frame_row
            # ok
            if 'access code'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 14)
                return data_frame_row
            # ok
            if 'no answer'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 14)
                return data_frame_row
            # ok
            if 'can\'t be reach'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 13)
                return data_frame_row
            # ok
            if 'cant be reach'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 13)
                return data_frame_row
            # ok
            if 'closed'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 14)
                return data_frame_row
            # ok
            if 'requested redelivery'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 23)
                return data_frame_row
            # ok
            if 'redelivery requested'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 23)
                return data_frame_row
            # ok
            if 'Cancel'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 20)
                return data_frame_row
            # ok
            if 'refused'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 19)

    # 如果是 SUCCEEDED 状态
    if data_frame_row['Drop off status'].values[0] == 'SUCCEEDED':
        # 先查看一些明显的问题
        if 'no access'.lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 14)
        elif 'no answer'.lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 14)
        elif 'no code'.lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 14)

        # 再看时间差，附着到之前的结果
        inbound_diff = date_subtract(data_frame_row['Inbound Scan Date (Linehaul)'].values[0],
                                     data_frame_row['Scheduled Delivery Date'].values[0])
        # 如果  inbound_diff 等于 0
        if inbound_diff == 0:
            # 如果 inbound 当天晚于 12 点
            if time_upper_than(data_frame_row['Inbound Scan Time'].values[0], '12:00', 0):
                data_frame_row['Inbound Comments'] = ['Inbound late']
                data_frame_row = copy_reason(data_frame_row, 24)
                return data_frame_row
            # 如果 inbound 当天早于 12 点
            else:
                get_pickup_and_delivery_status(data_frame_row, day, policy)

        # 如果 inbound_diff 大于一天
        elif inbound_diff > 0:
            data_frame_row['Inbound Comments'] = ['Inbound late']
            data_frame_row = copy_reason(data_frame_row, 24)
            # # 看 pick 减 inbound 的日子
            # pickup_diff = date_subtract(data_frame_row['Pickup Date'].values[0],
            #                             data_frame_row['Scheduled Delivery Date'].values[0]) - inbound_diff

            # inbound late 了，不看别的了
            # if pickup_diff > 0:
            #     if day == '3':
            #         data_frame_row = copy_reason(data_frame_row, 41)
            #         if pickup_diff == 1:
            #             # data_frame_row['Delivery Comments'] = [
            #             #     f'Inbound ontime but outbound late for 1 day']
            #             data_frame_row = write_in_delivery_comments(data_frame_row, f'Inbound late and outbound late for 1 day')
            #             data_frame_row['Pickup Comments'] = [
            #                 f'Inbound late and outbound late for 1 day']
            #             return data_frame_row
            #         else:
            #             # data_frame_row['Delivery Comments'] = [
            #             #     f'Inbound ontime but outbound late for {pickup_diff} days']
            #             data_frame_row = write_in_delivery_comments(data_frame_row, f'Inbound late and outbound late for {pickup_diff} days')
            #             data_frame_row['Pickup Comments'] = [
            #                 f'Inbound late and outbound late for {pickup_diff} days']
            #             return data_frame_row
            #     if day == '4':
            #         data_frame_row = copy_reason(data_frame_row, 0)
            #         if pickup_diff == 1:
            #             # data_frame_row['Delivery Comments'] = [
            #             #     f'Inbound ontime but outbound late for 1 day']
            #             data_frame_row = write_in_delivery_comments(data_frame_row, f'Inbound late and outbound late for 1 day')
            #             data_frame_row['Pickup Comments'] = [
            #                 f'Inbound late and outbound late for 1 day']
            #             return data_frame_row
            #         else:
            #             # data_frame_row['Delivery Comments'] = [
            #             #     f'Inbound ontime but outbound late for {pickup_diff} days']
            #             data_frame_row = write_in_delivery_comments(data_frame_row, f'Inbound late and outbound late for {pickup_diff} days')
            #             data_frame_row['Pickup Comments'] = [
            #                 f'Inbound late and outbound late for {pickup_diff} days']
            #             return data_frame_row
            #     return data_frame_row
            return data_frame_row

        # 当 Inbound 没 late
        else:
            get_pickup_and_delivery_status(data_frame_row, day, policy)

    return data_frame_row


def date_subtract(compared_date, schedule_date):
    if pd.isna(compared_date) or str(compared_date) == 'nan':
        return -100
    if pd.isna(schedule_date) or str(schedule_date) == 'nan':
        return -100
    else:
        try:
            print(compared_date, schedule_date)
            compared_date = datetime.datetime.strptime(compared_date, '%Y-%m-%d')
            # 如果 scheduled date 是月日年
            if is_mouth_day_year(schedule_date):
                schedule_date = datetime.datetime.strptime(schedule_date, '%m/%d/%Y')
            else:
                # print('卧槽尼玛', schedule_date)
                schedule_date = datetime.datetime.strptime(schedule_date, '%Y-%m-%d')
            return (compared_date - schedule_date).days
        except ValueError:
            return -100


def time_upper_than(time_str, upper, policy):
    upper_time = datetime.datetime.strptime(upper, '%H:%M')
    upper_time += datetime.timedelta(minutes=int(policy))
    time_str = datetime.datetime.strptime(time_str, '%H:%M')
    # print(upper_time, '-', time_str, '=', end=' ')
    # print(int(upper_time.strftime('%H%M')) - int(time_str.strftime('%H%M')))
    if (int(upper_time.strftime('%H%M')) - int(time_str.strftime('%H%M'))) > 0:
        return False
    else:
        return True


def write_in_delivery_comments(data_frame_row, string):
    if pd.isna(data_frame_row['Delivery Comments'].values[0]):
        data_frame_row['Delivery Comments'] = [string]
        return data_frame_row
    # 如果已经有了，就不管了
    elif string in data_frame_row['Delivery Comments'].values[0]:
        return data_frame_row
    else:
        # data_frame_row['Delivery Comments'] = [data_frame_row['Delivery Comments'].values[0] + '/' + string]
        data_frame_row['Delivery Comments'] = [string]
        return data_frame_row


def data_frame_row_time_change(data_frame_row):
    region = data_frame_row['Region Code'].values[0]

    try:
        if pd.isna(region):
            return data_frame_row

        # 判断 Region Code 属于那个地区
        elif region == 'CHI' or region == 'DFW' or region == 'HOU':
            # early 时间 latest 时间
            early_time_str = str(data_frame_row['Earliest Dropoff Time'].values[0])
            new_time = time_subtract(early_time_str, hours=2, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Earliest Dropoff Time'] = [new_time_str]

            latest_time_str = str(data_frame_row['Latest Dropoff Time'].values[0])
            new_time = time_subtract(latest_time_str, hours=2, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Latest Dropoff Time'] = [new_time_str]
            # 针对 inbound
            # 如果 时间有空的，跳过
            if pd.isna(data_frame_row['Inbound Scan Time'].values[0]):
                new_time = None
            else:
                inbound_time_str = str(data_frame_row['Inbound Scan Time'].values[0])
                new_time = time_subtract(inbound_time_str, hours=2, days=0)
                new_time_str = new_time.strftime('%H:%M')
                data_frame_row['Inbound Scan Time'] = [new_time_str]

            # 针对 pickup time
            if pd.isna(data_frame_row['Pickup Time'].values[0]):
                pass
            else:
                pickup_time_str = str(data_frame_row['Pickup Time'].values[0])
                new_pickup_time = time_subtract(pickup_time_str, hours=2, days=0)
                new_pickup_time_str = new_pickup_time.strftime('%H:%M')
                data_frame_row['Pickup Time'] = [new_pickup_time_str]

            # 针对 drop off time
            if pd.isna(data_frame_row['Drop off time'].values[0]):
                pass
            else:
                drop_time_str = str(data_frame_row['Drop off time'].values[0])
                new_drop_time = time_subtract(drop_time_str, hours=2, days=0)
                new_drop_time_str = new_drop_time.strftime('%H:%M')
                data_frame_row['Drop off time'] = [new_drop_time_str]

            # 如果前进了一天
            if new_time is None:
                return data_frame_row
            else:
                if str(new_time.date()) == '1899-12-31':
                    date_str = str(data_frame_row['Inbound Scan Date (Linehaul)'].values[0])

                    time_object = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    new_date = time_object - datetime.timedelta(days=1)
                    new_date_str = new_date.strftime('%Y-%m-%d')

                    data_frame_row['Inbound Scan Date (Linehaul)'] = [new_date_str]
                    return data_frame_row
                else:
                    return data_frame_row

        elif region == 'JFK' or region == 'PHL' or region == 'EWR':
            # early 时间 latest 时间
            early_time_str = str(data_frame_row['Earliest Dropoff Time'].values[0])
            new_time = time_subtract(early_time_str, hours=3, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Earliest Dropoff Time'] = [new_time_str]

            latest_time_str = str(data_frame_row['Latest Dropoff Time'].values[0])
            new_time = time_subtract(latest_time_str, hours=3, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Latest Dropoff Time'] = [new_time_str]
            # 针对 inbound
            # 如果 时间有空的，跳过
            if pd.isna(data_frame_row['Inbound Scan Time'].values[0]):
                new_time = None
            else:
                inbound_time_str = str(data_frame_row['Inbound Scan Time'].values[0])
                new_time = time_subtract(inbound_time_str, hours=3, days=0)
                new_time_str = new_time.strftime('%H:%M')
                data_frame_row['Inbound Scan Time'] = [new_time_str]

            # 针对 pickup time
            if pd.isna(data_frame_row['Pickup Time'].values[0]):
                pass
            else:
                pickup_time_str = str(data_frame_row['Pickup Time'].values[0])
                new_pickup_time = time_subtract(pickup_time_str, hours=3, days=0)
                new_pickup_time_str = new_pickup_time.strftime('%H:%M')
                data_frame_row['Pickup Time'] = [new_pickup_time_str]

            # 针对 drop off time
            if pd.isna(data_frame_row['Drop off time'].values[0]):
                pass
            else:
                drop_time_str = str(data_frame_row['Drop off time'].values[0])
                new_drop_time = time_subtract(drop_time_str, hours=3, days=0)
                new_drop_time_str = new_drop_time.strftime('%H:%M')
                data_frame_row['Drop off time'] = [new_drop_time_str]

            # 如果前进了一天
            if new_time is None:
                return data_frame_row
            else:
                if str(new_time.date()) == '1899-12-31':
                    date_str = str(data_frame_row['Inbound Scan Date (Linehaul)'].values[0])

                    time_object = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    new_date = time_object - datetime.timedelta(days=1)
                    new_date_str = new_date.strftime('%Y-%m-%d')

                    data_frame_row['Inbound Scan Date (Linehaul)'] = [new_date_str]
                    return data_frame_row
                else:
                    return data_frame_row

        elif region == 'PHX':
            # early 时间 latest 时间
            early_time_str = str(data_frame_row['Earliest Dropoff Time'].values[0])
            new_time = time_subtract(early_time_str, hours=1, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Earliest Dropoff Time'] = [new_time_str]

            latest_time_str = str(data_frame_row['Latest Dropoff Time'].values[0])
            new_time = time_subtract(latest_time_str, hours=1, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Latest Dropoff Time'] = [new_time_str]
            # 针对 inbound
            # 如果 时间有空的，跳过
            if pd.isna(data_frame_row['Inbound Scan Time'].values[0]):
                new_time = None
            else:
                inbound_time_str = str(data_frame_row['Inbound Scan Time'].values[0])
                new_time = time_subtract(inbound_time_str, hours=1, days=0)
                new_time_str = new_time.strftime('%H:%M')
                data_frame_row['Inbound Scan Time'] = [new_time_str]

            # 针对 pickup time
            if pd.isna(data_frame_row['Pickup Time'].values[0]):
                pass
            else:
                pickup_time_str = str(data_frame_row['Pickup Time'].values[0])
                new_pickup_time = time_subtract(pickup_time_str, hours=1, days=0)
                new_pickup_time_str = new_pickup_time.strftime('%H:%M')
                data_frame_row['Pickup Time'] = [new_pickup_time_str]

            # 针对 drop off time
            if pd.isna(data_frame_row['Drop off time'].values[0]):
                pass
            else:
                drop_time_str = str(data_frame_row['Drop off time'].values[0])
                new_drop_time = time_subtract(drop_time_str, hours=1, days=0)
                new_drop_time_str = new_drop_time.strftime('%H:%M')
                data_frame_row['Drop off time'] = [new_drop_time_str]

            # 如果前进了一天
            if new_time is None:
                return data_frame_row
            else:
                if str(new_time.date()) == '1899-12-31':
                    date_str = str(data_frame_row['Inbound Scan Date (Linehaul)'].values[0])

                    time_object = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    new_date = time_object - datetime.timedelta(days=1)
                    new_date_str = new_date.strftime('%Y-%m-%d')

                    data_frame_row['Inbound Scan Date (Linehaul)'] = [new_date_str]
                    return data_frame_row
                else:
                    return data_frame_row

        else:
            return data_frame_row
    except ValueError:
        return data_frame_row


def time_subtract(time_str, hours, days):
    time_object = datetime.datetime.strptime(time_str, '%H:%M')
    new_time = time_object - datetime.timedelta(hours=hours, days=days)
    return new_time


def change_Scheduled_Delivery_Date(data_frame_row):
    # if pd.isna(data_frame_row['Scheduled Delivery Date'][0]):
    #     return data_frame_row
    # else:
    s_date_str = data_frame_row['Scheduled Delivery Date'].values[0]
    if format_1(s_date_str):
        s_str = datetime.datetime.strptime(s_date_str, '%Y/%m/%d')
        s_str = s_str.strftime('%Y-%m-%d')
        data_frame_row['Scheduled Delivery Date'] = [s_str]
        return data_frame_row
    elif format_2(s_date_str):
        s_str = datetime.datetime.strptime(s_date_str, '%m/%d/%Y')
        s_str = s_str.strftime('%Y-%m-%d')
        data_frame_row['Scheduled Delivery Date'] = [s_str]
        return data_frame_row
    elif format_3(s_date_str):
        return data_frame_row
    else:
        return data_frame_row


def format_1(date):
    try:
        datetime.datetime.strptime(date, "%Y/%m/%d")
        return True
    except:
        return False


def format_2(date):
    try:
        datetime.datetime.strptime(date, "%m/%d/%Y")
        return True
    except:
        return False


def format_3(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return True
    except:
        return False


if __name__ == '__main__':
    d = '2021/2/2'
    g = datetime.datetime.strptime(d, '%Y/%m/%d')
    print(g)