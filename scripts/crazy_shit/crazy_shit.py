import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 要下载的网站URL
url = "https://banshi.beijing.gov.cn/"

# 创建保存目录
output_dir = "downloaded_site"
os.makedirs(output_dir, exist_ok=True)

# 请求网页内容
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# 下载页面上的所有静态资源（例如图片、CSS、JS文件）
for tag in soup.find_all(["img", "link", "script"]):
    if tag.name == "img" and tag.get("src"):
        src = tag.get("src")
    elif tag.name == "link" and tag.get("href"):
        src = tag.get("href")
    elif tag.name == "script" and tag.get("src"):
        src = tag.get("src")
    else:
        continue

    # 处理相对路径
    src_url = urljoin(url, src)

    # 获取文件名
    file_name = os.path.join(output_dir, os.path.basename(src_url))

    # 下载文件
    try:
        file_response = requests.get(src_url)
        with open(file_name, "wb") as f:
            f.write(file_response.content)
        print(f"Downloaded: {file_name}")
    except Exception as e:
        print(f"Failed to download {src_url}: {e}")

# 保存 HTML 文件
with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Download complete!")
