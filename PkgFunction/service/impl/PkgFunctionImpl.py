from openai import OpenAI
from flask import jsonify
from requirements import parse
import subprocess

# TODO 修改成合适的文件名或者包名
file_path = 'code/requirements.txt'

def getPkgName():
    with open(file_path, "r") as file:
        requirements_content = file.read()

    parsed_requirements = parse(requirements_content)
    package_names = [req.name for req in parsed_requirements]

    return list(set(package_names))

class PkgFunctionImpl:
    @staticmethod
    def getPkgFuncInfoByGpt():
        pkgName = getPkgName()
        print(pkgName)
        description = []
        description.append(f"您的项目使用的第三方包有:{', '.join(pkgName)}")
        for name in pkgName:
            try:
                
                client = OpenAI(
                    api_key="sk-YmqNIKPfCAGzR36F6Ku54dMd3Xz5xFHBS33Wep6BQdQof58p",
                    base_url="https://api.chatanywhere.tech/v1"
                )
                # TODO messages提示内容放到外部文件当中读取
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个了解python第三方包功能的助手"},
                        {"role": "system", "name": "example_user", "content": "请分点描述一下python的beautifulsoup4包的功能并用一句话总结"},
                        {"role": "system", "name": "example_assistant", 
                        "content": 
                        "1.解析HTML和XML: BeautifulSoup4可以帮助解析HTML和XML文档，提取其中的数据，例如标签、文本内容、属性等。\n" + 
                        "2.方便的导航和搜索: BeautifulSoup4提供了简单易用的方法来遍历文档的树形结构，以便快速定位到需要的信息。\n" + 
                        "3.支持多种解析器: BeautifulSoup4支持多种解析器，包括Python的内置解析器和第三方库，可以根据需要选择最合适的解析器。\n" + 
                        "4.支持多种外部库: BeautifulSoup4可以和其他库结合使用，例如Requests库用于获取网页内容，lxml库用于更快速的解析等。\n" + 
                        "5.数据格式化输出: BeautifulSoup4可以将解析后的数据格式化输出，方便查看和使用。\n" + 
                        "总结：BeautifulSoup4包用于解析HTML和XML文档，使得在Python中进行网页数据提取与操作更加方便。"},
                        {"role": "user", "content": f"请分点描述一下python的{name}包的功能并用一句话总结"},
                    ]
                )
                description.append(name+': '+completion.choices[0].message.content)
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个了解python第三方包功能的助手"},
                        {"role": "system", "name": "example_user", "content": "有没有其他包具有BeautifulSoup4的功能，能够替换BeautifulSoup4？给出一个例子即可"},
                        {"role": "system", "name": "example_assistant", 
                        "content": "lxml：高性能的 XML 和 HTML 处理库，支持 XPath 和 CSS 选择器。"},
                        {"role": "user", "content": f"有没有其他包具有{name}的功能，能够替换{name}？给出一个例子即可"},
                    ]
                )
                description.append(name+ '可替换包为: ' + completion.choices[0].message.content)
            except Exception as err:
                return jsonify({
                    "message": "error",
                    "status": 500,
                    "data": err
                }),500
        return jsonify({
                    "message": "Request processed successfully",
                    "status": 200,
                    "data": description
                }),200

    @staticmethod
    def generateRequirements():
            try:
                file = open('requirements.txt')
                print('requirements.txt already exists.')
                file.close()
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
                subprocess.check_output(["/home/ecs-user/anaconda3/envs/sitp/bin/pipreqs", "--encoding", "utf-8", "code"])
                #subprocess.check_output(["D:\\anaconda3\envs\sitp_scanner\Scripts\pipreqs.exe", "--encoding", "utf-8", "code"])
                print("Requirements generated successfully.")
            except subprocess.CalledProcessError as e:
                print("Failed to generate requirements:", e.output)