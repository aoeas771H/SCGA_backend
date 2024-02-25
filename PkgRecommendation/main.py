from flask import Flask, request, jsonify
from src.packageHelper import PypiPackageInfo
app = Flask(__name__)

@app.route('/pkgRecommendation', methods=['POST'])
def get_recommendation():
    data = request.json  # 获取JSON数据
    package_name = data.get('name', '')  # 从JSON中提取字符串
    page=PypiPackageInfo(package_name)
    state,reason,info=page.getInfo()
    return jsonify({'state': state, 'reason':reason,'description':info['gpt'],'score':info['recommendScore']})
    
    
if __name__ == '__main__':
    app.run(debug=True)
