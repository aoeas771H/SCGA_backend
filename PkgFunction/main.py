from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import os
from service.result import result
from service.impl.PkgFunctionImpl import *
import shutil

app = Flask(__name__)

@app.route('/test',methods=['GET'])
def test():
    return 'hello world'

def delete_folder(path):
    try:
        shutil.rmtree(path)
    except Exception as err:
        print(err)

class scan_requirements:
    # 接收前端传来的文件并分析出requirements得到包的功能描述
    @app.route('/pkgFunction',methods=['POST'])
    def getPkgFuncInfo():
        if not os.path.exists('code'):
            os.makedirs('code')
        uploaded_files = request.files.getlist('file')
        if len(uploaded_files) == 0:
            return result.error("No file part",500,err)
        
        try:
            for file in uploaded_files:
                if file.filename == '':
                    return result.error("No selected part",500,err)
                # 保存文件
                file.save('/home/ecs-user/sitp/code/'+file.filename)
                #file.save('E:\CollegeData\sitp\scanner\code\\' + file.filename)
            # 分析代码文件
            PkgFunctionImpl.generateRequirements()
            # 生成包的功能描述
            ans = PkgFunctionImpl.getPkgFuncInfoByGpt()
            print(ans)
            delete_folder('./code')
            return ans
        except Exception as err:
            return result.error("error",500,err)

test_requirements = scan_requirements()

if __name__ == '__main__':
    app.run()
    