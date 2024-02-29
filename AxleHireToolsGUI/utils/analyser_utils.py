# encoding: utf-8
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


def copy_reason(data_frame_row, index, rewrite=False):
    copy_df = DICT_DF[DICT_DF.index == index]
    # 如果全是空的，直接复制
    if not rewrite:
        if pd.isna(data_frame_row['POD Valid?'].values[0]) and pd.isna(data_frame_row['POD Quality'].values[0]) and \
                pd.isna(data_frame_row['Issue Category'].values[0]) and pd.isna(
            data_frame_row['Delivery Comments'].values[0]) and \
                pd.isna(data_frame_row['AH Assessment'].values[0]):
            data_frame_row['POD Valid?'] = [nan_to_none(copy_df['POD Valid?'].values[0])]
            data_frame_row['POD Quality'] = [nan_to_none(copy_df['POD Quality'].values[0])]
            data_frame_row['Issue Category'] = copy_df['Issue Category'].values
            data_frame_row['Delivery Comments'] = copy_df['Delivery Comments'].values
            data_frame_row['AH Assessment'] = copy_df['AH Assessment'].values

            return data_frame_row
        # 如果不是空的，加一个 / 再将内容附着上
        else:
            data_frame_row['POD Valid?'] = [nan_to_none(str(copy_df['POD Valid?'].values[0]))]
            data_frame_row['POD Quality'] = [nan_to_none(str(copy_df['POD Quality'].values[0]))]
            data_frame_row['Issue Category'] = [
                str(data_frame_row['Issue Category'].values[0]) + '/' + str(copy_df['Issue Category'].values[0])]
            data_frame_row['Delivery Comments'] = [
                str(data_frame_row['Delivery Comments'].values[0]) + '/' + str(copy_df['Delivery Comments'].values[0])]
            data_frame_row['AH Assessment'] = [
                str(data_frame_row['AH Assessment'].values[0]) + '/' + str(copy_df['AH Assessment'].values[0])]
            return data_frame_row

    if rewrite:
        data_frame_row['POD Valid?'] = [nan_to_none(copy_df['POD Valid?'].values[0])]
        data_frame_row['POD Quality'] = [nan_to_none(copy_df['POD Quality'].values[0])]
        data_frame_row['Issue Category'] = copy_df['Issue Category'].values
        data_frame_row['Delivery Comments'] = copy_df['Delivery Comments'].values
        data_frame_row['AH Assessment'] = copy_df['AH Assessment'].values

        return data_frame_row


def date_subtract(compared_date, schedule_date):
    if pd.isna(compared_date) or str(compared_date) == 'nan':
        return -100
    if pd.isna(schedule_date) or str(schedule_date) == 'nan':
        return -100
    else:
        try:
            compared_date = datetime.datetime.strptime(compared_date, '%Y-%m-%d')
            # 如果 scheduled date 是月日年
            if is_mouth_day_year(schedule_date):
                schedule_date = datetime.datetime.strptime(schedule_date, '%m/%d/%Y')
            else:
                schedule_date = datetime.datetime.strptime(schedule_date, '%Y-%m-%d')
            return (compared_date - schedule_date).days
        except ValueError:
            return -100


def time_upper_than(time_str, upper, policy):
    upper_time = datetime.datetime.strptime(upper, '%H:%M')
    upper_time += datetime.timedelta(minutes=int(policy))
    time_str = datetime.datetime.strptime(time_str, '%H:%M')
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
            early_time_str = str(data_frame_row['Earliest dropoff time'].values[0])
            new_time = time_subtract(early_time_str, hours=2, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Earliest dropoff time'] = [new_time_str]

            latest_time_str = str(data_frame_row['Latest dropoff time'].values[0])
            new_time = time_subtract(latest_time_str, hours=2, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Latest dropoff time'] = [new_time_str]
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
            early_time_str = str(data_frame_row['Earliest dropoff time'].values[0])
            new_time = time_subtract(early_time_str, hours=3, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Earliest dropoff time'] = [new_time_str]

            latest_time_str = str(data_frame_row['Latest dropoff time'].values[0])
            new_time = time_subtract(latest_time_str, hours=3, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Latest dropoff time'] = [new_time_str]
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
            early_time_str = str(data_frame_row['Earliest dropoff time'].values[0])
            new_time = time_subtract(early_time_str, hours=1, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Earliest dropoff time'] = [new_time_str]

            latest_time_str = str(data_frame_row['Latest dropoff time'].values[0])
            new_time = time_subtract(latest_time_str, hours=1, days=0)
            new_time_str = new_time.strftime('%H:%M')
            data_frame_row['Latest dropoff time'] = [new_time_str]
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


def get_status_2023_3_15(data_frame_row, day, policy):
    """
    本周的HF和F75做法有一些改动。请按照以下方法做：
    1、Inbound阶段，先做inbound missing，inbound damaged 以及inbound是空着的，空着的就写package not received by AX那个code就行。
    2、以上三部分做完后，开始看received OK那些时间。需要与客户的delivery date时间进行对比，如果晚了的，需要在inbound comments那里写上inbound late for XX days 或者SDLAX地区的写上 AX linehaul late for XX days。不管后面operation是什么情况，只要inbound late了，都要写上，不能空着。最后delivery comments那列也需要写上Inbound late for XX days, 不能只写“Inbound late”。
    3、然后看shipment status那一列，如果有cancelled before/after pickup或者GEOCODED的，可以先做好，以后就不用看了。
    4、然后开始看pickup阶段。
    1）pickup status “FAILED” ： 如果remark写的是cannot find，missing，cannot locate之类的，在pickup comments那里写“Pickup Missing”； 如果remark写的damaged，leaking之类的，pickup comments写“Pickup Damaged”； 如果remark写的 Missort或者看不出来是什么的，pickup comments写“Pickup Failed”. 如果pickup remark写的是“Received Damaged”，我们需要看Dropoff Reason和Remark那两列，如果Dropoff Reason是空的，Dropoff remark写的是received damaged，那后面就写not due to AX performance/Inbound Damaged的reason code就可以；如果Dropoff Reason写了“No Access Code”或者“Communication Issue”之类的，那就按我们做dropoff failed那些no access code或者cannot reach customer的方法做。
    2）pickup status "Ready" "Pending" 或者是空的，首先看inbound如果late了，那就不需要看history了，直接写Received Late。如果inbound 没有late，则需要我们一个一个看shipment history。 Pickup comments这列不能空着，如果没有可以用的remark或者reason，我们就写inbound ok but pickup failed或者pickup ok but delivery failed。这样我就能知道这种是history里没有显示什么信息了，我就不用再进去重新看了。不然空着的我每次都要进去重新看是不是有没贴的。
    3）最后看pickup succeeded那些的时间。如果有晚了的，不管dropoff是什么情况，只要pickup晚了都需要在comments那列表出来inbound ontime but outbound late for XX days. 晚了的不能空着。以后都不用看PIckup after 12PM了。
    4）注意：从这周开始，pickup late和dropoff late不能写not due to了，又换成以前的做法了。如果pickup late了，Issue那要改成“Operation”， delivery comments那里按pickup comments写Inound ontime but outbound late for XX day就可以，AH Assessment写“Pickup Late”就可以。
    5、然后开始看Dropoff阶段。
    1）Dropoff enroute, pending或者ready之类的，就按你们之前的做法就行，一般都是Delivery issue，pickup OK but delivery failed.
    2) Dropoff failed也是按照目前的做法就行；HF有一列客户给的说明，你们做的时候可以参考下，他们把客户有留言的都写在这里了。
    3）Dropoff suceeded的看时间的同pickup看时间一样，如果晚了的，写Delivery Issue，comments里面写pickup ok but delivery late for XX days, AH Assessment写Late
    4）看照片的时候主要注意看那些放在lobby, mail locker或者inside gate的那些，是不是客户有指定放在这些地方，也可以参考客户给的说明那一列。

    以上都做好后，请两位看下你们的列的顺序要跟上周的claim列的顺序保持一致，谢谢。
    """
    # 3. 然后看shipment status那一列，如果有cancelled before/after pickup或者GEOCODED的，可以先做好，以后就不用看了。
    if 'GEOCODED'.lower() in str(data_frame_row['Shipment status'].values[0]).lower():
        if pd.isna(data_frame_row['Inbound status'].values[0]):
            # Not Due to AX performance | Package not received by AxleHire | Package not received by AxleHire
            data_frame_row = copy_reason(data_frame_row, 27)
            return data_frame_row
        if 'missing'.lower() in str(data_frame_row['Inbound status'].values[0]).lower():
            # Not Due to AX performance | Inbound missing |	Received missing
            data_frame_row = copy_reason(data_frame_row, 25)
            data_frame_row['Inbound Comments'] = ['Inbound Missing']
            return data_frame_row
        if 'RECEIVED_OK'.lower() in str(data_frame_row['Inbound status'].values[0]).lower():
            # Not Due to AX performance | Inbound missing |	Received missing
            data_frame_row = copy_reason(data_frame_row, 29)
            return data_frame_row
    if 'CANCELLED_BEFORE_PICKUP'.lower() in str(data_frame_row['Shipment status'].values[0]).lower():
        # Not Due to AX performance	| Cancelled Order | Cancelled Order
        data_frame_row = copy_reason(data_frame_row, 20)
        return data_frame_row
    if 'GEOCODE_FAILED'.lower() in str(data_frame_row['Shipment status'].values[0]).lower():
        # Not Due to AX performance	| Out of delivery area	| Outside Service Area
        data_frame_row = copy_reason(data_frame_row, 22)
        return data_frame_row
    if 'UNSERVICEABLE'.lower() in str(data_frame_row['Shipment status'].values[0]).lower():
        # Not Due to AX performance	| Out of delivery area	| Outside Service Area
        data_frame_row = copy_reason(data_frame_row, 22)
        return data_frame_row

    # 1. Inbound阶段，先做inbound missing，inbound damaged 以及inbound是空着的，空着的就写package not received by AX那个code就行。
    if 'MISSING'.lower() in str(data_frame_row['Inbound status'].values[0]).lower():
        # Not Due to AX performance | Inbound missing |	Received missing
        data_frame_row = copy_reason(data_frame_row, 25)
        data_frame_row['Inbound Comments'] = ['Inbound Missing']

    if 'RECEIVED_DAMAGED'.lower() in str(data_frame_row['Inbound status'].values[0]).lower():
        # Not Due to AX performance | Inbound damage | Received damaged
        data_frame_row = copy_reason(data_frame_row, 26)
        data_frame_row['Inbound Comments'] = ['Inbound Damaged']

    if pd.isna(data_frame_row['Inbound status'].values[0]):
        # Not Due to AX performance | Package not received by AxleHire | Package not received by AxleHire
        data_frame_row = copy_reason(data_frame_row, 27)

    # 2. 以上三部分做完后，开始看received OK那些时间。需要与客户的delivery date时间进行对比，如果晚了的，
    # 需要在inbound comments那里写上inbound late for XX days 或者 SDLAX 地区的写上 AX linehaul late for XX days。
    # 不管后面operation是什么情况，只要inbound late了，都要写上，不能空着。
    # 最后delivery comments那列也需要写上Inbound late for XX days, 不能只写“Inbound late”。
    """
    判断 inbound ok 时，无法判断最终归因，不 return
    """
    if 'RECEIVED_OK'.lower() in str(data_frame_row['Inbound status'].values[0]).lower():
        inbound_diff = date_subtract(data_frame_row['Inbound Scan Date (Linehaul)'].values[0],
                                     data_frame_row['Scheduled Delivery Date'].values[0])
        # 如果 inbound 为当天
        if inbound_diff == 0:
            # 如果 inbound 当天晚于 12 点
            if time_upper_than(data_frame_row['Inbound Scan Time'].values[0], '12:00', 0):
                # 如果是 SDLAX
                if 'SDLAX'.lower() in str(data_frame_row['Region Code'].values[0]).lower():
                    # AX linehaul issue | AX linehaul late | Late
                    data_frame_row = copy_reason(data_frame_row, 28)
                    data_frame_row['Inbound Comments'] = ['AX linehaul late for same day']
                    # change AX linehaul late -> AX linehaul late for same day
                    data_frame_row['Delivery Comments'] = ['AX linehaul late for same day']
                # 除 SDLAX 以外的 Region
                else:
                    # Not Due to AX performance | Inbound late | Received late
                    data_frame_row = copy_reason(data_frame_row, 24)
                    data_frame_row['Inbound Comments'] = ['Inbound late for same day']
                    # change Inbound late -> Inbound late for same day
                    data_frame_row['Delivery Comments'] = ['Inbound late for same day']
        # 如果 inbound 晚于 1 或以上天
        if inbound_diff > 0:
            # 2天以上需要加小尾巴
            tails = '' if inbound_diff == 1 else 's'
            # 如果是 SDLAX
            if 'SDLAX'.lower() in str(data_frame_row['Region Code'].values[0]).lower():
                # AX linehaul issue | AX linehaul late | Late
                data_frame_row = copy_reason(data_frame_row, 28)
                data_frame_row['Inbound Comments'] = [f'AX linehaul late for {inbound_diff} day{tails}']
                # change AX linehaul late -> AX linehaul late for same day
                data_frame_row['Delivery Comments'] = [f'AX linehaul late for {inbound_diff} day{tails}']
            # 除 SDLAX 以外的 Region
            else:
                # Not Due to AX performance | Inbound late | Received late
                data_frame_row = copy_reason(data_frame_row, 24)
                data_frame_row['Inbound Comments'] = [f'Inbound late for {inbound_diff} day{tails}']
                # change Inbound late -> Inbound late for same day
                data_frame_row['Delivery Comments'] = [f'Inbound late for {inbound_diff} day{tails}']

    # 4. 然后开始看pickup阶段。
    # 1）pickup status “FAILED” ： 如果remark写的是cannot find，missing，cannot locate之类的，
    # 在pickup comments那里写“Pickup Missing”； 如果remark写的damaged，leaking之类的，pickup comments写“Pickup Damaged”；
    # 如果remark写的 Missort或者看不出来是什么的，pickup comments写“Pickup Failed”. 如果pickup remark写的是“Received Damaged”，
    # 我们需要看Dropoff Reason和Remark那两列，如果Dropoff Reason是空的，Dropoff remark写的是received damaged，
    # 那后面就写not due to AX performance/Inbound Damaged的reason code就可以；
    # 如果Dropoff Reason写了“No Access Code”或者“Communication Issue”之类的，
    # 那就按我们做dropoff failed那些no access code或者cannot reach customer的方法做。
    if 'FAILED'.lower() in str(data_frame_row['Pickup Status'].values[0]).lower():
        # 尽可能罗列出 pickup missing 的更多的选项
        if 'cannot find'.lower() in str(data_frame_row['Pickup remark'].values[0]).lower() or \
                'missing'.lower() in str(data_frame_row['Pickup remark'].values[0]).lower() or \
                'cannot locate'.lower() in str(data_frame_row['Pickup remark'].values[0]).lower():
            data_frame_row['Pickup Comments'] = ['Pickup Missing']
        # 尽可能罗列出 pickup damage 的更多的选项
        if 'damaged'.lower() in str(data_frame_row['Pickup remark'].values[0]).lower() or \
                'leaking'.lower() in str(data_frame_row['Pickup remark'].values[0]).lower():
            data_frame_row['Pickup Comments'] = ['Pickup Damaged']
        # 尽可能罗列出 pickup failed 的更多的选项
        if 'Missort'.lower() in str(data_frame_row['Pickup remark'].values[0]).lower() or \
                '.'.lower() in str(data_frame_row['Pickup remark'].values[0]).lower():
            data_frame_row['Pickup Comments'] = ['Pickup Failed']

    # 2）pickup status "Ready" "Pending" 或者是空的，首先看inbound如果late了，那就不需要看history了，直接写Received Late。
    # 如果inbound 没有late，则需要我们一个一个看shipment history。 Pickup comments这列不能空着，如果没有可以用的remark或者reason，
    # 我们就写inbound ok but pickup failed或者pickup ok but delivery failed。这样我就能知道这种是history里没有显示什么信息了，
    # 我就不用再进去重新看了。不然空着的我每次都要进去重新看是不是有没贴的。
    if 'READY'.lower() in str(data_frame_row['Pickup Status'].values[0]).lower() or \
            'PENDING'.lower() in str(data_frame_row['Pickup Status'].values[0]).lower() or \
            pd.isna(data_frame_row['Pickup Status'].values[0]):
        # 首先看inbound如果late了，那就不需要看history了，直接写Received Late
        inbound_diff = date_subtract(data_frame_row['Inbound Scan Date (Linehaul)'].values[0],
                                     data_frame_row['Scheduled Delivery Date'].values[0])
        # 如果 inbound 为当天
        if inbound_diff == 0:
            # 如果 inbound 当天晚于 12 点
            if time_upper_than(data_frame_row['Inbound Scan Time'].values[0], '12:00', 0):
                # 如果是 SDLAX
                if 'SDLAX'.lower() in str(data_frame_row['Region Code'].values[0]).lower():
                    # AX linehaul issue | AX linehaul late | Late
                    data_frame_row = copy_reason(data_frame_row, 28, rewrite=True)
                    data_frame_row['Inbound Comments'] = ['AX linehaul late for same day']
                    # change AX linehaul late -> AX linehaul late for same day
                    data_frame_row['Delivery Comments'] = ['AX linehaul late for same day']
                    return data_frame_row
                # 除 SDLAX 以外的 Region
                else:
                    # Not Due to AX performance | Inbound late | Received late
                    data_frame_row = copy_reason(data_frame_row, 24, rewrite=True)
                    data_frame_row['Inbound Comments'] = ['Inbound late for same day']
                    # change Inbound late -> Inbound late for same day
                    data_frame_row['Delivery Comments'] = ['Inbound late for same day']
                    return data_frame_row
        # 如果 inbound 晚于 1 或以上天
        if inbound_diff > 0:
            # 2天以上需要加小尾巴
            tails = '' if inbound_diff == 1 else 's'
            # 如果是 SDLAX
            if 'SDLAX'.lower() in str(data_frame_row['Region Code'].values[0]).lower():
                # AX linehaul issue | AX linehaul late | Late
                data_frame_row = copy_reason(data_frame_row, 28, rewrite=True)
                data_frame_row['Inbound Comments'] = [f'AX linehaul late for {inbound_diff} day{tails}']
                # change AX linehaul late -> AX linehaul late for same day
                data_frame_row['Delivery Comments'] = [f'AX linehaul late for {inbound_diff} day{tails}']
                return data_frame_row
            # 除 SDLAX 以外的 Region
            else:
                # Not Due to AX performance | Inbound late | Received late
                data_frame_row = copy_reason(data_frame_row, 24, rewrite=True)
                data_frame_row['Inbound Comments'] = [f'Inbound late for {inbound_diff} day{tails}']
                # change Inbound late -> Inbound late for same day
                data_frame_row['Delivery Comments'] = [f'Inbound late for {inbound_diff} day{tails}']
                return data_frame_row

        # 如果 inbound 没 late，写入提示
        data_frame_row['Pickup Comments'] = ['需要看shipment history'] if pd.isna(
            data_frame_row['Issue Category'].values[0]) else ['']

    # 3）最后看pickup succeeded那些的时间。如果有晚了的，不管dropoff是什么情况，
    # 只要pickup晚了都需要在comments那列表出来inbound ontime but outbound late for XX days. 晚了的不能空着。以后都不用看PIckup after 12PM了。
    if 'SUCCEEDED'.lower() in str(data_frame_row['Pickup Status'].values[0]).lower() and \
            data_frame_row['Drop off status'].values[0] != 'FAILED':
        pickup_diff = date_subtract(data_frame_row['Pickup Date'].values[0],
                                    data_frame_row['Scheduled Delivery Date'].values[0])
        print(pickup_diff, 'diff')
        inbound_diff = date_subtract(data_frame_row['Inbound Scan Date (Linehaul)'].values[0],
                                     data_frame_row['Scheduled Delivery Date'].values[0])
        # pickup 只看晚于 1 天的，且 inbound 不晚
        if inbound_diff < 0 or (
                inbound_diff == 0 and not time_upper_than(data_frame_row['Inbound Scan Time'].values[0], '12:00', 0)):
            if pickup_diff > 0:
                tails = '' if pickup_diff == 1 else 's'
                # Operation	| Inbound ontime but outbound late for 1 day | Missort
                data_frame_row = copy_reason(data_frame_row, 41, rewrite=True)
                data_frame_row['Pickup Comments'] = [f'Inbound ontime but outbound late for {pickup_diff} day{tails}']
                data_frame_row['Delivery Comments'] = [
                    f'Inbound ontime but outbound late for {pickup_diff} day{tails}']
                data_frame_row['AH Assessment'] = [f'Pickup Late']

    # 4）注意：从这周开始，pickup late和dropoff late不能写not due to了，又换成以前的做法了。
    # 如果pickup late了，Issue那要改成“Operation”， delivery comments那里按pickup comments写Inound ontime but outbound late for XX day就可以，
    # AH Assessment写“Pickup Late”就可以。

    # 5、然后开始看Dropoff阶段。
    # 1）Dropoff enroute, pending或者ready之类的，就按你们之前的做法就行，一般都是Delivery issue，pickup OK but delivery failed.
    if data_frame_row['Drop off status'].values[0] == 'DISCARDED':
        if "Damaged".lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 34, rewrite=True)
        if 'RECEIVED_DAMAGED'.lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 26, rewrite=True)
            data_frame_row['Inbound Comments'] = ['Inbound Damaged']
        if 'discard'.lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 37, rewrite=True)
        if "Missing".lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 35, rewrite=True)
        if pd.isna(data_frame_row['Drop off remark'].values[0]):
            data_frame_row = copy_reason(data_frame_row, 52, rewrite=True)

    if data_frame_row['Drop off status'].values[0] is None:
        if 'missing by inbound' in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 25, rewrite=True)
            data_frame_row['Inbound Comments'] = ['Inbound Missing']
        if 'missing by outbound' in str(data_frame_row['Drop off remark'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 35, rewrite=True)

    if data_frame_row['Drop off status'].values[0] == 'EN_ROUTE':
        if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
            data_frame_row = copy_reason(data_frame_row, 52, rewrite=True)

    if data_frame_row['Drop off status'].values[0] == 'PENDING':
        if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
            data_frame_row = copy_reason(data_frame_row, 52, rewrite=True)
        if data_frame_row['Pickup Status'].values[0] == 'FAILED' or \
                data_frame_row['Pickup Status'].values[0] == 'PENDING':
            data_frame_row = copy_reason(data_frame_row, 31, rewrite=True)

    # 2) Dropoff failed也是按照目前的做法就行；HF有一列客户给的说明，你们做的时候可以参考下，他们把客户有留言的都写在这里了。
    if data_frame_row['Drop off status'].values[0] == 'FAILED':
        # ok
        if pd.isna(data_frame_row['Drop off remark'].values[0]):
            data_frame_row = copy_reason(data_frame_row, 52, rewrite=True)
            return data_frame_row
        # 如果 remark 不是空
        if isinstance(data_frame_row['Drop off remark'].values[0], str):
            # ok
            if 'out of cold chain'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 51, rewrite=True)
                return data_frame_row
            # ok
            if 'damaged'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 46, rewrite=True)
                return data_frame_row
            # ok
            if 'requested redelivery'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 23, rewrite=True)
                return data_frame_row
            # ok
            if 'redelivery requested'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 23, rewrite=True)
                return data_frame_row
            # ok
            if 'Cancel'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 20, rewrite=True)
                return data_frame_row
            # ok
            if 'refused'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 19, rewrite=True)
                return data_frame_row
            # ok
            if 'Customer requested Redelivery'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 14, rewrite=True)
                return data_frame_row
            # ok
            if 'RECEIVER_DECLINED_DELIVERY'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                data_frame_row = copy_reason(data_frame_row, 19, rewrite=True)
                return data_frame_row

    # 3）Dropoff suceeded的看时间的同pickup看时间一样，如果晚了的，写Delivery Issue，comments里面写pickup ok but delivery late for XX days, AH Assessment写Late
    if data_frame_row['Drop off status'].values[0] == 'SUCCEEDED':
        pickup_diff = date_subtract(data_frame_row['Pickup Date'].values[0],
                                    data_frame_row['Scheduled Delivery Date'].values[0])
        inbound_diff = date_subtract(data_frame_row['Inbound Scan Date (Linehaul)'].values[0],
                                     data_frame_row['Scheduled Delivery Date'].values[0])
        delivery_diff = date_subtract(data_frame_row['Drop off date'].values[0],
                                      data_frame_row['Pickup Date'].values[0])
        # 重新看 inbound
        if 'RECEIVED_OK'.lower() in str(data_frame_row['Inbound status'].values[0]).lower():
            # 如果 inbound 为当天
            if inbound_diff == 0:
                # 如果 inbound 当天晚于 12 点
                if time_upper_than(data_frame_row['Inbound Scan Time'].values[0], '12:00', 0):
                    # 如果是 SDLAX
                    if 'SDLAX'.lower() in str(data_frame_row['Region Code'].values[0]).lower():
                        # AX linehaul issue | AX linehaul late | Late
                        data_frame_row = copy_reason(data_frame_row, 28, rewrite=True)
                        data_frame_row['Inbound Comments'] = ['AX linehaul late for same day']
                        # change AX linehaul late -> AX linehaul late for same day
                        data_frame_row['Delivery Comments'] = ['AX linehaul late for same day']
                        return data_frame_row
                    # 除 SDLAX 以外的 Region
                    else:
                        # Not Due to AX performance | Inbound late | Received late
                        data_frame_row = copy_reason(data_frame_row, 24, rewrite=True)
                        data_frame_row['Inbound Comments'] = ['Inbound late for same day']
                        # change Inbound late -> Inbound late for same day
                        data_frame_row['Delivery Comments'] = ['Inbound late for same day']
                        return data_frame_row
            # 如果 inbound 晚于 1 或以上天
            if inbound_diff > 0:
                # 2天以上需要加小尾巴
                tails = '' if inbound_diff == 1 else 's'
                # 如果是 SDLAX
                if 'SDLAX'.lower() in str(data_frame_row['Region Code'].values[0]).lower():
                    # AX linehaul issue | AX linehaul late | Late
                    data_frame_row = copy_reason(data_frame_row, 28, rewrite=True)
                    data_frame_row['Inbound Comments'] = [f'AX linehaul late for {inbound_diff} day{tails}']
                    # change AX linehaul late -> AX linehaul late for same day
                    data_frame_row['Delivery Comments'] = [f'AX linehaul late for {inbound_diff} day{tails}']
                    return data_frame_row
                # 除 SDLAX 以外的 Region
                else:
                    # Not Due to AX performance | Inbound late | Received late
                    data_frame_row = copy_reason(data_frame_row, 24, rewrite=True)
                    data_frame_row['Inbound Comments'] = [f'Inbound late for {inbound_diff} day{tails}']
                    # change Inbound late -> Inbound late for same day
                    data_frame_row['Delivery Comments'] = [f'Inbound late for {inbound_diff} day{tails}']
                    return data_frame_row

        # 重新看 pickup
        if 'SUCCEEDED'.lower() in str(data_frame_row['Pickup Status'].values[0]).lower():

            # pickup 只看晚于 1 天的，且 inbound 不晚
            if inbound_diff < 0 or (
                    inbound_diff == 0 and not time_upper_than(data_frame_row['Inbound Scan Time'].values[0], '12:00',
                                                              0)):
                if pickup_diff > 0:
                    tails = '' if pickup_diff == 1 else 's'
                    # Operation	| Inbound ontime but outbound late for 1 day | Missort
                    data_frame_row = copy_reason(data_frame_row, 41, rewrite=True)
                    data_frame_row['Pickup Comments'] = [
                        f'Inbound ontime but outbound late for {pickup_diff} day{tails}']
                    data_frame_row['Delivery Comments'] = [
                        f'Inbound ontime but outbound late for {pickup_diff} day{tails}']
                    data_frame_row['AH Assessment'] = [f'Pickup Late']

        # drop 在当天
        if delivery_diff == 0:
            if time_upper_than(data_frame_row['Drop off time'].values[0],
                               data_frame_row['Latest dropoff time'].values[0], policy):
                # 如果 drop 当天晚了，pickup 也晚了
                if pickup_diff > 0:
                    tails = '' if pickup_diff == 1 else 's'
                    # Operation	| Inbound ontime but outbound late for 1 day | Missort
                    data_frame_row = copy_reason(data_frame_row, 41, rewrite=True)
                    data_frame_row['Pickup Comments'] = [
                        f'Inbound ontime but outbound late for {pickup_diff} day{tails}']

                    data_frame_row['AH Assessment'] = [f'Pickup Late']

                    data_frame_row = copy_reason(data_frame_row, 118, rewrite=True)
                    data_frame_row['Delivery Comments'] = [f'pickup late for {pickup_diff} day{tails} '
                                                           f'and delivery late for same day']
                else:
                    # 如果 drop 当天晚了， pickup 没晚
                    data_frame_row = copy_reason(data_frame_row, 118, rewrite=True)
                    data_frame_row['Delivery Comments'] = [f'pickup ok but delivery late for same day']

        # drop 晚于一天
        if delivery_diff > 0:
            if time_upper_than(data_frame_row['Drop off time'].values[0],
                               data_frame_row['Latest dropoff time'].values[0], policy):
                # 如果 drop 配送时间晚了，pickup 也晚了
                if pickup_diff > 0:
                    tails = '' if pickup_diff == 1 else 's'
                    # Operation	| Inbound ontime but outbound late for 1 day | Missort
                    data_frame_row = copy_reason(data_frame_row, 41, rewrite=True)
                    data_frame_row['Pickup Comments'] = [
                        f'Inbound ontime but outbound late for {pickup_diff} day{tails}']
                    data_frame_row['AH Assessment'] = [f'Pickup Late']

                    data_frame_row = copy_reason(data_frame_row, 118, rewrite=True)
                    data_frame_row['Delivery Comments'] = [f'pickup late for {pickup_diff} day{tails} '
                                                           f'and delivery late for same day']
                    return data_frame_row
                # 如果 drop 配送时间晚了， pickup 没晚
                else:
                    data_frame_row = copy_reason(data_frame_row, 118, rewrite=True)
                    data_frame_row['Delivery Comments'] = [f'pickup ok but delivery late for same day']
                    return data_frame_row
            # drop 只日期晚了
            else:
                delivery_tails = '' if delivery_diff == 1 else 's'
                if pickup_diff > 0:
                    tails = '' if pickup_diff == 1 else 's'
                    # Operation	| Inbound ontime but outbound late for 1 day | Missort
                    data_frame_row = copy_reason(data_frame_row, 41, rewrite=True)
                    data_frame_row['Pickup Comments'] = [
                        f'Inbound ontime but outbound late for {pickup_diff} day{tails}']
                    data_frame_row['AH Assessment'] = [f'Pickup Late']

                    data_frame_row = copy_reason(data_frame_row, 118, rewrite=True)
                    data_frame_row['Delivery Comments'] = [f'pickup late for {pickup_diff} day{tails} '
                                                           f'and delivery late for {delivery_diff} day{delivery_tails}']
                    return data_frame_row
                # 如果 drop 配送时间晚了， pickup 没晚
                data_frame_row = copy_reason(data_frame_row, 118, rewrite=True)
                data_frame_row['Delivery Comments'] = [
                    f'pickup ok but delivery late for {delivery_diff} day{delivery_tails}']
                return data_frame_row

    # 4）看照片的时候主要注意看那些放在lobby, mail locker或者inside gate的那些，是不是客户有指定放在这些地方，也可以参考客户给的说明那一列。

    return data_frame_row