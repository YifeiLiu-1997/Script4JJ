import pandas as pd
import utils.analyser_utils as analyser_utils


class Thursday(object):
    def __init__(self, init_df):
        self.init_df = init_df

    def analyse(self):
        res_data = self.init_df.copy()
        result = pd.DataFrame(columns=res_data.columns)
        for index, row in self.init_df.iterrows():
            # 填入 week √
            temp = analyser_utils.get_week_num(res_data.iloc[index: index+1, :])
            # 分析 shipment_status √
            temp = analyser_utils.get_shipment_status(temp)
            # 分析 drop off status
            res_data.iloc[index: index + 1, :] = analyser_utils.get_drop_off_status(temp)
            result = pd.concat([result, temp])
        result['Updated Reason Code'] = result['AH Assessment']
        return result


if __name__ == '__main__':
    init_df = pd.read_csv('files/20211027-152332.csv')
    thursday = Thursday(init_df)
    res_df = thursday.analyse()
    res_df.to_excel('test.xlsx')
    # dict_df = pd.read_excel('files/dictionary.xlsx')

