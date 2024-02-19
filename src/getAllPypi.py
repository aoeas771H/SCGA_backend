import requests
from packageHelper import PypiPackageInfo
from tqdm import tqdm
from datetime import datetime
# def get_pypi_packages():
#     response = requests.get('https://pypi.org/simple/')
#     if response.status_code == 200:
#         # 解析返回的HTML，提取包名
#         package_names = [line.split('>')[1].split('<')[0] for line in response.text.split('\n') if line.startswith('<a href=')]
#         return package_names
#     else:
#         print("无法连接到PyPI")
#         return []
    
def month_diff(target_date):
    current_date = datetime.now()
    year_diff = current_date.year - target_date.year
    month_diff = current_date.month - target_date.month

    total_months = year_diff * 12 + month_diff
    return total_months
   
def save_packages_to_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        unique_lines =file.readlines()
    with open(output_file, 'a', encoding='utf-8') as file:
        with open("error-1.txt",'a',encoding='utf-8') as errfile: 
            for package_name in tqdm(unique_lines):
                
                    package_name=package_name[:-1] 
                    print(package_name)
                    page=PypiPackageInfo(package_name)
                    state,reason,data=page.getInfo()

                    if state:
                        content=package_name+' ' +str(state)+ ' '+str(reason) +' '+str(data['updateScore'])+' '+str(data['solveScore'])+' '+str(data['hotScore'])+' '+str(data['maintenanceScore'])+' '+str(data['recommendScore'])+"\n"
                    
                    else:
                        content=package_name+' ' +str(state)+ ' '+str(reason)+"\n"   
                    print(content)
                    file.write(content)
                
            
save_packages_to_file("output-1.txt","data-2.txt")

 
