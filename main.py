import requirements
import yaml
from flask import Flask
import json
import requests
from bs4 import BeautifulSoup
import subprocess
import os
import re
from git import Repo
import pkg_resources

app = Flask(__name__)

class scan_requirements:
    @staticmethod
    def get_range(conditions):
        min_version = None
        max_version = None

        for condition in conditions:
            operators = ["<=", "<", ">=", ">"]
            operator = None
            for op in operators:
                if op in condition:
                    operator = op
                    break

            if operator is not None:
                version = condition.split(operator)[1].strip()
                if operator == ">=":
                    if min_version is None or version > min_version:
                        min_version = version
                elif operator == "<":
                    if max_version is None or version < max_version:
                        max_version = version
                elif operator == "<=":
                    if max_version is None or version <= max_version:
                        max_version = version
                elif operator == ">":
                    if min_version is None or version >= min_version:
                        min_version = version

        range_condition = ""
        if min_version is not None:
            range_condition += f"Python >= {min_version}"
        if max_version is not None:
            if range_condition != "":
                range_condition += ", "
            range_condition += f"Python < {max_version}"

        return range_condition
    
    @staticmethod
    def analysis_pyversion(req):
        url = f"https://pypi.org/project/{req.name}/"
        response = requests.get(url)
        content = response.text
        soup = BeautifulSoup(content, "html.parser")
        pyversion = soup.find_all("p")
        for i in range(len(pyversion)):
            version = pyversion[i].text.strip()
            if "Requires" in version:
                return str(version).replace("Requires: ","")
    
    @staticmethod
    def analysis_latest(req):
        ret = []
        # 对于requirements当中的每一个序列进行分析
        # 初步设想先把每一个包获取其官网的最新版本号
        url = f"https://pypi.org/project/{req.name}/"
        # 发起 GET 请求获取页面内容
        response = requests.get(url)
        content = response.text
        # 解析 html 页面
        soup = BeautifulSoup(content, "html.parser")
        # 定位到版本号标签，并提取最新版本号，和最新版发布时间
        version_tag = soup.find("p", class_="release__version")
        version_time = soup.find("time")
        latest_version_no = version_tag.text.strip()
        latest_version_time = version_time.text.strip()
        ret.append({
            'latest_no': latest_version_no,
            'latest_time': latest_version_time
        })
        return ret
        
    @staticmethod
    def analysis_now(req):
        url = f"https://pypi.org/project/{req.name}/"
        response = requests.get(url)
        content = response.text
        soup = BeautifulSoup(content, "html.parser")
        target_version = req.specs[0][1]
        all_version = soup.find_all("p", class_="release__version")
        for i in range(len(all_version)):
            version_text = all_version[i].text.strip()
            if version_text == target_version:
                # 获取与指定版本号对应的发布时间
                time = soup.find_all("p", class_="release__version-date")[i].find("time")
                ret = time.text.strip()
                break
            else:
                ret = "N/A"
        return ret
    
    @app.route('/generate_requirements')
    def generate_requirements():
        try:
            file = open('requirements.txt')
            print('requirements.txt already exists.')
            file.close()
            return scan_requirements.requirements()
        except FileNotFoundError:
            print('requirements.txt does not exist.')
        except Exception as e:
            print('error:', str(e))
        try:
            # 用pipreqs包生成一个简单的requirements文件
            # 进行简单的代码预处理
            print('start generate requirements.txt')
            # TODO
            # 这里的pipreqs.exe如果要发布到服务器上则需要更改为服务器的可执行文件路径
            # . 表示当前文件夹下所有代码文件，后续要按要求做出更改
            subprocess.check_output(["D:\\anaconda3\envs\sitp_scanner\Scripts\pipreqs.exe", "--encoding", "utf-8", "."])
            print("Requirements generated successfully.")
        except subprocess.CalledProcessError as e:
            print("Failed to generate requirements:", e.output)
        return scan_requirements.requirements()
    
    @app.route('/scan_requirements')
    def requirements():
        # 最终要返回的可序列化的字典列表
        ret = []
        version_conditions = []
        with open("requirements.txt","r", encoding='utf-8') as file:
            content = file.read()
            for req in list(requirements.parse(content)):
                print("start scanning")
                now_info = []
                version_conditions.append(scan_requirements.analysis_pyversion(req))
                now_info.append({
                    'name': req.name,
                    'specs': req.specs,
                    'now_time': scan_requirements.analysis_now(req),
                })
                ret.append({
                    'now_info': now_info,
                    'latest_info': scan_requirements.analysis_latest(req)})
        ret.append([scan_requirements.get_range(version_conditions)])
        return json.dumps(ret)
        
class scan_yaml:
    ret = []
    def readDict(self,data):
        # TODO 将读取的yml文件内容进行清洗，整理出与版本信息或环境配置信息有关的内容
        for key,value in data.items():
            if isinstance(value, dict):
                self.readDict(value)
            else:
                # TODO 先字符串硬匹配，yaml文件当中会有什么版本信息呢？
                keyWords = ['python','version']
                if str(key) in keyWords:
                    self.ret.append({key:value})
    
    def yaml(self):
        with open("main.yml", "r", encoding='utf-8') as file:
            data = yaml.safe_load(file)
        self.readDict(data)
        print(json.dumps(self.ret))
        return json.dumps(self.ret)
          
class scan_code:
    @app.route('/get_github_code')
    def get_github_code():
        # TODO 测试从github拉取代码，先写死拉取网址和输出文件夹，后续要与前端对接
        github_url = "https://github.com/pallets/flask"
        saveDir = "E:\CollegeData\githubCode"
        Repo.clone_from(github_url,saveDir)
        return f"成功拉取github项目到: {saveDir}"
    
    @app.route('/extract_comments')
    def extract_comments_from_folder():
        # TODO 先把输入文件夹路径和输出文件名固定，后续再调整
        folder_path = 'D:\\anaconda3\envs\sitp_scanner\Lib\site-packages\\flask'
        output_file = 'comments.txt'
        
        comments = []
        python_files = [f for f in os.listdir(folder_path) if f.endswith(".py")]

        for file in python_files:
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r') as f:
                code = f.read()
                pattern = r"(#(.*)$)|(#(.*?)$|('''(.|\n)*?'''))"
                matches = re.finditer(pattern, code, re.MULTILINE)
                
                for match in matches:
                    comment = match.group().strip()
                    comments.append(comment)
        
        with open(output_file, 'w') as f:
            for comment in comments:
                f.write(comment)
                f.write('\n')
        return f"注释已成功写入到文件：{output_file}"
            
def get_package_dependencies(package_name): # 获得已安装的包的依赖关系
    try:
        # 获取指定包的分发信息
        distribution = pkg_resources.get_distribution(package_name)
        # 获取依赖关系
        dependencies = [str(req) for req in distribution.requires()]
        return dependencies
    except pkg_resources.DistributionNotFound:
        print(f"Package '{package_name}' not found.")
        return []
    # 用法示例
    '''
    package_name = "gym"
    dependencies = get_package_dependencies(package_name)

    print(f"Dependencies for {package_name}:")
    for dependency in dependencies:
        print(dependency)
    '''

test_requirements = scan_requirements()
test_yaml = scan_yaml()

if __name__ == '__main__':
    app.run()
    