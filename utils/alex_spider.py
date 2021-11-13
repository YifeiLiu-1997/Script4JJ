import requests
import json

from requests_ntlm import HttpNtlmAuth


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
    return result_dict['results'][0]


def get_all_report_csv():
    # url = 'https://dataorch-report.beta.axlehire.com/reports/all?clients=49%2C168&from=1634918400&to=1635263999'
    # url = 'https://dataorch-report.beta.axlehire.com/reports/all?clients=4&from=1635750000&to=1636009199'
    url = 'https://dataorch-report.beta.axlehire.com/reports/all?clients=185&from=1635577200&to=1636009199'
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'content-type': 'application/json',
        'cookie': r'fp=1a39e1225ea764ca9f2abf599fafba34; xtoken="dE9DbW1wYkZDI/B28g5MkirtzwljFDty7THWI75r/mVq4do8YKOJBeUtONSQ1d3L1Yb5JCAEZPTk\012FFj7LXpbKjSaV71j1S6I9zjtTLurIi1ddgqe+xsIRU84cjg0Sktu\012"'}

    session = requests.Session()
    user = 'yanxia.ji'
    password = 'Axl12345'
    response = session.get(url=url, headers=header, auth=HttpNtlmAuth(user, password))
    print(response.content)
    return response.text


if __name__ == '__main__':
    # print(get_dict_from_tracking_code(
    #     tracking_code='xut2dsejgvwwsh46'
    # ))
    print(get_all_report_csv())