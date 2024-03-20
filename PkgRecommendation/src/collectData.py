import datetime
import numpy as np

from githubUtils import GithubRepo
from pypiUtils import PypiProject
from gptUtils import GPTClient
from getSynk import getHealthScore
import pandas as pd
from tqdm import tqdm

def month_diff(target_date):
    try:
        # print(target_date)
        current_date = datetime.datetime.now()
        year_diff = current_date.year - target_date.year
        month_diff = current_date.month - target_date.month

        total_months = year_diff * 12 + month_diff
        return total_months
    except:
        return -1


class PackageInfo:

    def __init__(self, packageName: str):
        self.packageName = packageName
        self.pypiProject: 'PypiProject' = PypiProject(packageName)
        self.githubRepo: 'GithubRepo | None' = None

    def getInfo(self,df):
        """
        return state, reason, data
        
        """
        
        self.info = {}
        self.info['gpt'] = None
        self.info['recommendScore'] = None
        try:
            self.pypiProject.loadJson()
        except:
            return df

        self.info['versionList'] = self.pypiProject.getVersionList()

        self.info['averageUpdateInterval'] = self.getAverageUpdateInterval()

 
        try:
            self.githubRepo = GithubRepo(*self.pypiProject.getGithubAuthorAndRepoName())
        except Exception as e:
            print(e)
            pass

        if self.githubRepo is None:
            return df

        openCount, closeCount = self.githubRepo.getIssueCount()
        
        solveRate=closeCount/(closeCount+openCount+1)

        sumCount = closeCount + openCount
        lastCommitTime = self.githubRepo.getLastCommitTime()
 

        month_away=month_diff(lastCommitTime)
        
        synkScore=getHealthScore(self.packageName).split("/")[0]
        
        infolist=[self.packageName, self.info['averageUpdateInterval'], solveRate,sumCount,month_away,synkScore]
        print(infolist)
        df=df._append(pd.Series(infolist, index=df.columns), ignore_index=True)
        
        return df

 
 

 



    def getAverageUpdateInterval(self):
        """
        计算并返回平均更新间隔（以天为单位）。
        """

        version_list = self.info['versionList']
        if not version_list:
            return None

        # 确保版本列表按时间排序
        version_list.sort(key=lambda x: x.versionTime)

        # 计算相邻版本之间的时间间隔
        intervals = [
            (version_list[i].versionTime - version_list[i - 1].versionTime).days
            for i in range(1, len(version_list))
        ]

        if not intervals:
            return -1

        # 计算平均间隔
        average_interval = sum(intervals) / len(intervals)
        return average_interval
    
    
if __name__ == "__main__":

    df = pd.DataFrame(columns=['Name', 'averageUpdateInterval', 'solveRate','sumCount','month_away','synkScore'])
    
    input_file = "output-2.txt"
   
    with open(input_file, 'r', encoding='utf-8') as file:
        unique_lines =file.readlines()
        
        for package_name in tqdm(unique_lines):
                
            package_name=package_name[:-1] 
            print(package_name)
            page=PackageInfo(package_name)
            df=page.getInfo(df)

             
            df.to_excel("synk_info_3.xlsx",index=False)
             
 