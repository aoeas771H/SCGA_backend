import requests
from bs4 import BeautifulSoup

# 目标URL
url = 'https://snyk.io/advisor/python/matplotlib'

# 发送HTTP GET请求
response = requests.get(url)

# 确认请求成功
if response.status_code == 200:
    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 选择并提取需要的信息，这里以提取页面标题为例
    title = soup.find('title').get_text()
    print(title)
else:
    print("Failed to retrieve the webpage")