import requests
from packageHelper import PypiPackageInfo
from tqdm import tqdm
def get_pypi_packages():
    response = requests.get('https://pypi.org/simple/')
    if response.status_code == 200:
        # 解析返回的HTML，提取包名
        package_names = [line.split('>')[1].split('<')[0] for line in response.text.split('\n') if line.startswith('<a href=')]
        return package_names
    else:
        print("无法连接到PyPI")
        return []
    
def save_packages_to_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        unique_lines =file.readlines()
    with open(output_file, 'w', encoding='utf-8') as file:
        for package_name in tqdm(unique_lines):
            #print(package_name[::-1])
            page=PypiPackageInfo(package_name[:-1])
            openIssue,closeIssue=page.getIssueCount()
            file.write(package_name+' ' +str(openIssue)+ ' '+str(closeIssue) + '\n')
            
save_packages_to_file("output.txt","data.txt")

 
