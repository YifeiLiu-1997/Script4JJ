from analyser_utils import copy_reason


def analyse_status(data_frame_row, day):
    if data_frame_row['Shipment status'].values[0] == 'GEOCODED':
        data_frame_row = copy_reason(data_frame_row, 29)
        return data_frame_row
    elif 'canceled'.lower() in str(data_frame_row['Shipment status'].values[0]).lower():
        data_frame_row = copy_reason(data_frame_row, 20)
        return data_frame_row
    elif 'geocoded_failed'.lower() in str(data_frame_row['Shipment status'].values[0]).lower():
        data_frame_row = copy_reason(data_frame_row, 22)
        return data_frame_row
    else:
        if data_frame_row['Inbound status'].values[0] == 'MISSING':
            data_frame_row = copy_reason(data_frame_row, 25)
            return data_frame_row
        elif 'DAMAGED'.lower() in str(data_frame_row['Inbound status'].values[0]).lower():
            data_frame_row = copy_reason(data_frame_row, 26)
            return data_frame_row
        else:
            if day == '3':
                if 'fail' in str(data_frame_row['Pickup Status'].values[0]).lower():
                    data_frame_row = copy_reason(data_frame_row, 37)
                    return data_frame_row
                elif 'missing' in str(data_frame_row['Pickup Status'].values[0]).lower():
                    data_frame_row = copy_reason(data_frame_row, 35)
                    return data_frame_row
                elif 'damaged' in str(data_frame_row['Pickup Status'].values[0]).lower():
                    data_frame_row = copy_reason(data_frame_row, 34)
                    return data_frame_row
                else:
                    # 如果 dropoff remark 是空的
                    if pd.isna(data_frame_row['Drop off remark'].values[0]) or data_frame_row['Drop off remark'].values[
                        0] is None:
                        if 'SUCCEEDED'.lower() not in str(data_frame_row['Drop off status'].values[0]):
                            data_frame_row = copy_reason(data_frame_row, 52)
                            return data_frame_row
                    elif 'refuse'.lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
                        data_frame_row = copy_reason(data_frame_row, 19)
                        return data_frame_row
                    # 如果 dropoff remark 不是空的
                    else:
                        if data_frame_row['Drop off status'].values[0] == 'DISCARDED':
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
                                    if day == '4':
                                        data_frame_row = copy_reason(data_frame_row, 4)
                                        return data_frame_row
                                    elif day == '3':
                                        data_frame_row = copy_reason(data_frame_row, 35)
                                        return data_frame_row

                        if data_frame_row['Drop off status'].values[0] == 'EN_ROUTE':
                            if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
                                data_frame_row = copy_reason(data_frame_row, 52)
                                return data_frame_row
                            if data_frame_row['Pickup Status'].values[0] == 'FAILED':
                                if day == '4':
                                    data_frame_row = copy_reason(data_frame_row, 3)
                                    return data_frame_row
                                elif day == '3':
                                    data_frame_row = copy_reason(data_frame_row, 37)
                                    return data_frame_row

                        if data_frame_row['Drop off status'].values[0] == 'PENDING':
                            if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
                                data_frame_row = copy_reason(data_frame_row, 52)
                                return data_frame_row
                            if data_frame_row['Pickup Status'].values[0] == 'FAILED':
                                if day == '4':
                                    data_frame_row = copy_reason(data_frame_row, 3)
                                    return data_frame_row
                                elif day == '3':
                                    data_frame_row = copy_reason(data_frame_row, 37)
                                    return data_frame_row

                        if data_frame_row['Drop off status'].values[0] == 'FAILED':
                            if isinstance(data_frame_row['Drop off remark'].values[0], str):
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
                                if 'requested redelivery'.lower() in data_frame_row['Drop off remark'].values[
                                    0].lower():
                                    data_frame_row = copy_reason(data_frame_row, 23)
                                    return data_frame_row
                                if 'redelivery requested'.lower() in data_frame_row['Drop off remark'].values[
                                    0].lower():
                                    data_frame_row = copy_reason(data_frame_row, 23)
                                    return data_frame_row
                                if 'Cancel'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                                    data_frame_row = copy_reason(data_frame_row, 20)
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
                                    pickup_diff = date_subtract(data_frame_row['Pickup Date'].values[0],
                                                                data_frame_row['Scheduled Delivery Date'].values[0])
                                    if pickup_diff >= 0:
                                        if pickup_diff == 0:
                                            if time_upper_than(data_frame_row['Pickup Time'].values[0], '12:00'):
                                                print('Pickup Time', data_frame_row['Pickup Time'].values[0])
                                                data_frame_row['Pickup Comments'] = ['Pickup after 12pm']
                                        else:
                                            data_frame_row = copy_reason(data_frame_row, 2)
                                            if pickup_diff == 1:
                                                data_frame_row['Pickup Comments'] = [
                                                    f'outbound late for {pickup_diff} day']
                                            else:
                                                data_frame_row['Pickup Comments'] = [
                                                    f'outbound late for {pickup_diff} days']
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
                                            if pickup_diff == 1:
                                                data_frame_row['Pickup Comments'] = [
                                                    f'outbound late for {pickup_diff} day']
                                            else:
                                                data_frame_row['Pickup Comments'] = [
                                                    f'outbound late for {pickup_diff} days']
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
                                        data_frame_row = copy_reason(data_frame_row, 41)
                                        if pickup_diff == 1:
                                            data_frame_row['Delivery Comments'] = [
                                                f'Inbound ontime but outbound late for {pickup_diff} day']
                                            data_frame_row['Pickup Comments'] = [
                                                f'Inbound ontime but outbound late for {pickup_diff} day']
                                        else:
                                            data_frame_row['Delivery Comments'] = [
                                                f'Inbound ontime but outbound late for {pickup_diff} days']
                                            data_frame_row['Pickup Comments'] = [
                                                f'Inbound ontime but outbound late for {pickup_diff} days']
                                else:
                                    delivery_diff = date_subtract(data_frame_row['Drop off date'].values[0],
                                                                  data_frame_row['Pickup Date'].values[0])
                                    if delivery_diff == 0:
                                        if time_upper_than(data_frame_row['Drop off time'].values[0],
                                                           data_frame_row['Latest Dropoff Time'].values[0]):
                                            data_frame_row = copy_reason(data_frame_row, 118)
                                            return data_frame_row
                                    else:
                                        data_frame_row = copy_reason(data_frame_row, 119)
                                        if delivery_diff == 1:
                                            data_frame_row['Delivery Comments'] = [
                                                f'pickup ok but delivery late for {delivery_diff} day']
                                        else:
                                            data_frame_row['Delivery Comments'] = [
                                                f'pickup ok but delivery late for {delivery_diff} days']
                                        return data_frame_row
                return data_frame_row
            elif day == '4':
                if 'fail' in str(data_frame_row['Pickup Status'].values[0]).lower():
                    data_frame_row = copy_reason(data_frame_row, 3)
                    return data_frame_row
                elif 'missing' in str(data_frame_row['Pickup Status'].values[0]).lower():
                    data_frame_row = copy_reason(data_frame_row, 4)
                    return data_frame_row
                elif 'damaged' in str(data_frame_row['Pickup Status'].values[0]).lower():
                    data_frame_row = copy_reason(data_frame_row, 5)
                    return data_frame_row
                else:
                    # 如果 dropoff remark 是空的
                    if pd.isna(data_frame_row['Drop off remark'].values[0]) or data_frame_row['Drop off remark'].values[
                        0] is None:
                        if 'SUCCEEDED'.lower() not in str(data_frame_row['Drop off status'].values[0]):
                            data_frame_row = copy_reason(data_frame_row, 52)
                            return data_frame_row
                    elif 'refuse'.lower() in str(data_frame_row['Drop off remark'].values[0]).lower():
                        data_frame_row = copy_reason(data_frame_row, 19)
                        return data_frame_row
                    # 如果 dropoff remark 不是空的
                    else:
                        if data_frame_row['Drop off status'].values[0] == 'DISCARDED':
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
                                    if day == '4':
                                        data_frame_row = copy_reason(data_frame_row, 4)
                                        return data_frame_row
                                    elif day == '3':
                                        data_frame_row = copy_reason(data_frame_row, 35)
                                        return data_frame_row

                        if data_frame_row['Drop off status'].values[0] == 'EN_ROUTE':
                            if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
                                data_frame_row = copy_reason(data_frame_row, 52)
                                return data_frame_row
                            if data_frame_row['Pickup Status'].values[0] == 'FAILED':
                                if day == '4':
                                    data_frame_row = copy_reason(data_frame_row, 3)
                                    return data_frame_row
                                elif day == '3':
                                    data_frame_row = copy_reason(data_frame_row, 37)
                                    return data_frame_row

                        if data_frame_row['Drop off status'].values[0] == 'PENDING':
                            if data_frame_row['Pickup Status'].values[0] == 'SUCCEEDED':
                                data_frame_row = copy_reason(data_frame_row, 52)
                                return data_frame_row
                            if data_frame_row['Pickup Status'].values[0] == 'FAILED':
                                if day == '4':
                                    data_frame_row = copy_reason(data_frame_row, 3)
                                    return data_frame_row
                                elif day == '3':
                                    data_frame_row = copy_reason(data_frame_row, 37)
                                    return data_frame_row

                        if data_frame_row['Drop off status'].values[0] == 'FAILED':
                            if isinstance(data_frame_row['Drop off remark'].values[0], str):
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
                                if 'Cancel'.lower() in data_frame_row['Drop off remark'].values[0].lower():
                                    data_frame_row = copy_reason(data_frame_row, 20)
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
                                    pickup_diff = date_subtract(data_frame_row['Pickup Date'].values[0],
                                                                data_frame_row['Scheduled Delivery Date'].values[0])
                                    if pickup_diff >= 0:
                                        if pickup_diff == 0:
                                            if time_upper_than(data_frame_row['Pickup Time'].values[0], '12:00'):
                                                print('Pickup Time', data_frame_row['Pickup Time'].values[0])
                                                data_frame_row['Pickup Comments'] = ['Pickup after 12pm']
                                        else:
                                            data_frame_row = copy_reason(data_frame_row, 42)
                                            if pickup_diff == 1:
                                                data_frame_row['Pickup Comments'] = [
                                                    f'outbound late for {pickup_diff} day']
                                            else:
                                                data_frame_row['Pickup Comments'] = [
                                                    f'outbound late for {pickup_diff} days']
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
                                            if pickup_diff == 1:
                                                data_frame_row['Pickup Comments'] = [f'outbound late for {pickup_diff} day']
                                            else:
                                                data_frame_row['Pickup Comments'] = [
                                                    f'outbound late for {pickup_diff} days']
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
                                        if pickup_diff == 1:
                                            data_frame_row['Delivery Comments'] = [
                                                f'Inbound ontime but outbound late for {pickup_diff} day']
                                            data_frame_row['Pickup Comments'] = [
                                                f'Inbound ontime but outbound late for {pickup_diff} day']
                                        else:
                                            data_frame_row['Delivery Comments'] = [
                                                f'Inbound ontime but outbound late for {pickup_diff} days']
                                            data_frame_row['Pickup Comments'] = [
                                                f'Inbound ontime but outbound late for {pickup_diff} days']
                                else:
                                    delivery_diff = date_subtract(data_frame_row['Drop off date'].values[0],
                                                                  data_frame_row['Pickup Date'].values[0])
                                    if delivery_diff == 0:
                                        if time_upper_than(data_frame_row['Drop off time'].values[0],
                                                           data_frame_row['Latest Dropoff Time'].values[0]):
                                            data_frame_row = copy_reason(data_frame_row, 118)
                                            return data_frame_row
                                    else:
                                        data_frame_row = copy_reason(data_frame_row, 119)
                                        if delivery_diff == 1:
                                            data_frame_row['Delivery Comments'] = [
                                                f'pickup ok but delivery late for {delivery_diff} day']
                                        else:
                                            data_frame_row['Delivery Comments'] = [
                                                f'pickup ok but delivery late for {delivery_diff} days']
                                        return data_frame_row
                return data_frame_row
        return data_frame_row