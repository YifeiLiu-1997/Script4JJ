import requests
import json
from requests_ntlm import HttpNtlmAuth


class DownLoader(object):
    def __init__(self, root=None):
        self.root = root
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/95.0.4638.69 Safari/537.36',
            'content-type': 'application/json',
            'cookie': r'fp=1a39e1225ea764ca9f2abf599fafba34; xtoken="dE9DbW1wYkZDI/B28g5MkirtzwljFDty7THWI75r/mVq4do8Y'
                      r'KOJBeUtONSQ1d3L1Yb5JCAEZPTk\012FFj7LXpbKjSaV71j1S6I9zjtTLurIi1ddgqe+xsIRU84cjg0Sktu\012"'
        }
        self.user_name = 'yanxia.ji'
        self.password = 'Axl12345'

    def get_csv_from_date(self, client_id, date):
        url_format = f'https://dataorch-report.beta.axlehire.com/reports/all?clients={client_id}&date={date}'
        session = requests.Session()
        response = session.get(url=url_format, headers=self.header, auth=HttpNtlmAuth(self.user_name, self.password))
        print(response.text)
        with open('test.csv', 'wb') as fp:
            fp.write(response.content)

    @staticmethod
    def get_dict_from_tracking_code(tracking_code):
        url = 'https://dataorch.axlehire.com/shipments/search'
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'content-type': 'application/json',
            'cookie': r'fp=1a39e1225ea764ca9f2abf599fafba34; xtoken="dE9DbW1wYkZDI/B28g5MkirtzwljFDty7THWI75r/mVq4do8YKOJBeUtONSQ1d3L1Yb5JCAEZPTk\012FFj7LXpbKjSaV71j1S6I9zjtTLurIi1ddgqe+xsIRU84cjg0Sktu\012"'}
        # 生成 post 的 json_data
        data_dict = {'size': 15, 'q': tracking_code,
                     'filters': {}, 'sorts': ['-dropoff_earliest_ts']}
        json_data = json.dumps(data_dict)

        session = requests.Session()
        user = 'yanxia.ji'
        password = 'Axl12345'
        response = session.post(url=url, headers=header, data=json_data, auth=HttpNtlmAuth(user, password))

        result_dict = json.loads(response.text)
        return result_dict


if __name__ == '__main__':
    downloader = DownLoader()
    # downloader.get_csv_from_date(client_id='159', date='2021-10-19')2021-10-19
    print(downloader.get_dict_from_tracking_code('SCD1970110400304388'))
