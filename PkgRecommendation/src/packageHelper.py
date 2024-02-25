from abc import ABC, abstractmethod
from openai import OpenAI
from flask import jsonify
import requests
import datetime
import src.githubUtils
import numpy as np
def month_diff(target_date):
    # print(target_date)
    current_date = datetime.datetime.now()
    year_diff = current_date.year - target_date.year
    month_diff = current_date.month - target_date.month

    total_months = year_diff * 12 + month_diff
    return total_months


class IPackageInfo(ABC):
    @abstractmethod
    def getRecommendScore(self) -> float:
        pass


# 一次更新的信息
class ReleaseInfo:
    def __init__(self, versionName: str, versionTime: datetime.datetime):
        self.versionName = versionName
        self.versionTime = versionTime


# 输入一个pypi中有的包名，输出其最近几个版本的更新时间。藉由此，我们可以评估出这个包的更新频率
class PypiPackageInfo(IPackageInfo):
    # github issue界面的筛选表达式，前面的open或者close会自动加上
    githubIssueFilterSuffix = "error"

    def __init__(self, packageName: str):
        self.closeCount = None
        self.openCount = None
        self.packageName = packageName
        self.__pypiJson__: 'dict | None' = None

        self.__authorName__: 'str | None' = None
        self.__repoName__: 'str | None' = None

        self.__cachedReleaseList__: 'list[ReleaseInfo] | None' = None
        self.__cachedIssueCount__: 'tuple[int,int] | None' = None
        self.__cachedLastCommitTime__: 'datetime | None' = None

    def getInfo(self):
        """
        return state, reason, data
        
        """
        print(self.packageName+"syffffffffff")
        self.info = {}
        self.info['gpt']=None
        self.info['recommendScore']=None
        try:
            self.__loadJson__()
        except:
            return 0, "Network error or Package not found", self.info
        
        self.description="请用中文回答我的以下问题：我有一个python第三方包，"
        
        self.info['versionList']=self.getVersionList()

        self.info['averageUpdateInterval']=self.getAverageUpdateInterval()
        self.description=self.description+"它的版本更新频率是"+self.info['averageUpdateInterval']+"天，"
        updateScore=180/self.info['averageUpdateInterval']#小于一年的更新频率，就拿10分
        self.info['updateScore']=updateScore=min(1,max(updateScore,0.2))*10

        #bamboo
        """
        bamboo
        pyxhook
        PytorchNLP
        mistune
        drone
        mars
        """
        
        if self.__authorName__ is None:
            return 0, "Not a Github-based project!", self.info
        
        self.getIssueCount()
        
        self.sumCount=self.closeCount+self.openCount
        self.info['solveScore']=solveScore=self.closeCount/max(1,self.sumCount)*10
        self.description=self.description+"它的github库中close的issue为"+str(self.closeCount)+"，open的issue为"+str(self.openCount)+"，"
        
        hotScore=np.sqrt(self.sumCount/10)
        self.info['hotScore']=hotScore=min(10,max(hotScore,2))

        lastCommitTime=self.getLastCommitTime()
        maintenanceScore=9-month_diff(lastCommitTime)/2
        self.description=self.description+"它的最后一次commit时间为"+lastCommitTime.strftime("%Y-%m-%d %H:%M:%S")
        self.info['maintenanceScore']=maintenanceScore=min(10,max(maintenanceScore,2))
        
         
        self.info['recommendScore']=3*updateScore+2.5*solveScore+2*hotScore+2.5*maintenanceScore
        
        self.info['gpt']=self.getDescription()
        
        return 1, "ok", self.info
    def getDescription(self):
            try:
                print(self.description)
                gptDescription = ""
                client = OpenAI(
                    api_key="sk-YmqNIKPfCAGzR36F6Ku54dMd3Xz5xFHBS33Wep6BQdQof58p",
                    base_url="https://api.chatanywhere.tech/v1"
                )    
                
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个了解python第三方包功能的助手"},
                        {"role": "user", "content": f"{self.description},请从更新频率，解决问题的可能性，维护程度，该包的流行程度这4个方面，定性地描述这个包。"},
                    ]
                )
                
                gptDescription=completion.choices[0].message.content
            except Exception as err:
                return  {
                    "message": "error",
                    "status": 500,
                    "data": err
                } 
            return  {
                    "message": "Request processed successfully",
                    "status": 200,
                    "data": gptDescription
                } 
                
        
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
   

    def __loadJson__(self):
        url = "https://pypi.org/pypi/{}/json".format(self.packageName)
        res = requests.get(url)
        self.__pypiJson__ = res.json()
        if 'info' not in self.__pypiJson__:
            if 'message' in self.__pypiJson__:
                raise Exception(self.__pypiJson__['message'])
            raise Exception('Package not found')

        projectUrls = self.__pypiJson__['info']['project_urls']
        for key in projectUrls:
            if projectUrls[key].find("github.com") > 0:
                issueLinkKey = key
                self.__authorName__, self.__repoName__ = githubUtils.extractAuthorAndRepoName(projectUrls[issueLinkKey])
                if self.__authorName__ is not None:
                    break

    def getVersionList(self):
        """

        :return: 返回该包每次发布的版本号与发布时间
        """
        if self.__cachedReleaseList__ is not None:
            return self.__cachedReleaseList__

        if self.__pypiJson__ is None:
            self.__loadJson__()

        ans: 'list[ReleaseInfo]' = []
        for versionName, obj in self.__pypiJson__['releases'].items():
            if len(obj) < 1:
                continue
            timeStr: str = obj[-1]['upload_time_iso_8601']

            # 解决pypi日期不规范的问题
            if timeStr.find(".") > -1:
                t = datetime.datetime.strptime(obj[-1]['upload_time_iso_8601'], '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                t = datetime.datetime.strptime(obj[-1]['upload_time_iso_8601'], '%Y-%m-%dT%H:%M:%SZ')
            ans.append(ReleaseInfo(versionName, t))

        self.__cachedReleaseList__ = ans
        return ans

    def getIssueCount(self):
        """

        :return: 返回条件下的open,closed状态的issue数量
        """
        if self.__pypiJson__ is None:
            self.__loadJson__()

        if self.__cachedIssueCount__ is not None:
            return self.__cachedIssueCount__

        if self.__authorName__ is None:
            raise Exception("Not a Github-based project!")

        self.openCount = githubUtils.getIssueCount(self.__authorName__, self.__repoName__, "is:open " + self.githubIssueFilterSuffix)
        self.closeCount = githubUtils.getIssueCount(self.__authorName__, self.__repoName__, "is:closed " + self.githubIssueFilterSuffix)

        self.__cachedIssueCount__ = self.openCount, self.closeCount
        return self.__cachedIssueCount__

    def getLastCommitTime(self):
        if self.__pypiJson__ is None:
            self.__loadJson__()

        if self.__cachedLastCommitTime__ is not None:
            return self.__cachedLastCommitTime__

        if self.__authorName__ is None:
            raise Exception("Not a Github-based project!")

        ans = githubUtils.getLatestCommitTime(self.__authorName__, self.__repoName__)
        return ans

    def getRecommendScore(self) -> float:
        """
        计算包的推荐指数
        :return:
        """
        # TODO
        return 100.0


if __name__ == "__main__":
    page = PypiPackageInfo("pydantic")
    print(page.getVersionList())
    print(page.getLastCommitTime())
    print(page.getIssueCount())
    

