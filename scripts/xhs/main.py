import re
from pathlib import Path
import os
from bs4 import BeautifulSoup
import requests
from io import BytesIO


'''https://ci.xiaohongshu.com/ 这个是小红书无水印拼接链接，后面只要传入：traceId 里面的参数即可'''


def fetchUrl(url):
    '''
    发起网络请求，获取网页源码
    '''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9 ',
        'cookie': '',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36',
    }

    r = requests.get(url, headers=headers)
    return r.text


def parsing_link(html):
    '''
    解析html文本，提取无水印图片的 url
    '''

    imageList = get_real_png_url(html)
    return imageList


def get_real_png_url(webp_html):
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(webp_html, 'html.parser')

    # 查找所有meta标签
    meta_tags = soup.find_all('meta')

    # 提取og:image的内容
    og_images = [tag['content'] for tag in meta_tags if tag.get('name') == 'og:image']

    real_png_images = []
    for img_url in og_images:
        real_img_url = generate_png_link(extract_image_token(img_url))
        real_png_images.append(real_img_url)

    return real_png_images


def generate_png_link(token: str) -> str:
    return f"https://ci.xiaohongshu.com/{token}?imageView2/format/png"


def extract_image_token(url: str) -> str:
    return "/".join(url.split("/")[5:]).split("!")[0]


def download(url, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36',
    }

    with open(f'{filename}.jpg', 'wb') as v:
        try:
            r = requests.get(url, headers=headers)
            v.write(r.content)
        except Exception as e:
            print('图片下载错误！')


def get_img_url_list_from_short_url(source_txt):
    # 使用正则表达式匹配URL
    short_url = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                           source_txt)

    if short_url:
        html = fetchUrl(short_url[0])
        real_img_url_list = parsing_link(html)
        return real_img_url_list

    else:
        print("No URL found")


if __name__ == '__main__':
    urls = get_img_url_list_from_short_url(
        source_txt='99 拾叁发布了一篇小红书笔记，快来看吧！ 😆 Es7dbq4pO6nPWuA 😆 http://xhslink.com/a/yJni2AWMqfEZ，复制本条信息，打开【小红书】App查看精彩内容！'
    )

    # 指定下载路径
    download_path = Path('./小狗/')

    # 确保下载路径存在
    download_path.mkdir(parents=True, exist_ok=True)

    # 遍历URL列表并下载图片
    for i, url in enumerate(urls):
        try:
            response = requests.get(url)
            response.raise_for_status()  # 确保请求成功

            # 构建文件名，例如：image1.jpg
            file_name = f'image_{i + 1}.jpg'
            file_path = download_path / file_name

            # 写入图片数据到文件
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f'图片已下载：{file_path}')
        except requests.RequestException as e:
            print(f'下载失败：{url}，错误信息：{e}')
