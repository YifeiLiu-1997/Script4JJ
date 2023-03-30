import pandas as pd
import AxleParsingTools.utils.analyser_utils as analyser_utils
import tqdm


class Wednesday(object):
    def __init__(self, init_df, policy):
        self.init_df = init_df
        self.policy = policy

    def analyse(self):
        res_data = self.init_df.copy()
        res_data.rename(columns={'HF Reason Code': 'AH Assessment', 'POD Qaulity': 'POD Quality'}, inplace=True)
        result = pd.DataFrame(columns=res_data.columns)
        for index, row in tqdm.tqdm(self.init_df.iterrows(), desc='分析中'):
            # 修改 Scheduled Delivery Date 成为 %Y-%m-%d
            temp = analyser_utils.change_Scheduled_Delivery_Date(res_data.iloc[index: index + 1, :])
            # 填入 week √
            temp = analyser_utils.get_week_num(temp)
            # 分析 status in 2023-3-15
            res_data.iloc[index: index + 1, :] = analyser_utils.get_status_2023_3_15(temp, day='3', policy=self.policy)
            result = pd.concat([result, temp])
        result['Updated Reason Code'] = result['AH Assessment']
        return result
