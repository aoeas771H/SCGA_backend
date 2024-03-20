import requests
from bs4 import BeautifulSoup

def getHealthScore(package_name):
    # 网页URL
    url = 'https://snyk.io/advisor/python/' + package_name

    # 发送HTTP请求
    response = requests.get(url)

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    score_span = soup.find('span', {'data-v-3f4fee08': True})
    if score_span:
        return score_span.text  # 返回分数
    else:
        return "分数未找到"
 