import os
from flask import Flask, request, jsonify
from src.packageHelper import PackageInfo

app = Flask(__name__)

"""
请求结构：
{
    "name":"flask"
}
返回：
{
    "state":1成功，0 失败
    "reason":字符串，可以在失败的时候显示原因
    "description":gpt的描述与评价(state为1 时可信)
    "score":推荐的分数(state为1 时可信)
}

"""

def textHelp(score,text):
    if score<3:
        return "该包的"+text+"较低"
    elif score<7:
        return "该包的"+text+"适中"
    else:
        return "该包的"+text+"较高" 

@app.route('/pkgRecommendation', methods=['POST'])
def get_recommendation():
    data = request.json  # 获取JSON数据
    package_name = data.get('name', '')  # 从JSON中提取字符串
    page = PackageInfo(package_name)
    state, reason, info = page.getInfo()
    return jsonify({'state': state, 'reason': reason, 'description': info['gpt'], 'score': info['recommendScore'],
                    'hotScore':info['hotScore'],'hotScoreText':textHelp(info['hotScore'],"热度"),
                    'updateScore':info['updateScore'],'updateScoreText':textHelp(info['updateScore'],"更新频率"),
                    'solveScore':info['solveScore'],'solveScoreText':textHelp(info['solveScore'],"问题解决率"),
                    'maintenanceScore':info['maintenanceScore'],'maintenanceScoreText':textHelp(info['maintenanceScore'],"维护程度") })


if __name__ == '__main__':
    app.run(debug=True)
