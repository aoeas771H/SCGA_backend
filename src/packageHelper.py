from abc import ABC, abstractmethod

import requests
import datetime
import githubUtils

def month_diff(target_date):
    #print(target_date)
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
        self.info={}
        try:
            self.__loadJson__()
        except:
            return 0, "Network error or Package not found", self.info
        
         
        
        self.info['versionList']=self.getVersionList()
        self.info['averageUpdateInterval']=self.getAverageUpdateInterval()
        updateScore=360/self.info['averageUpdateInterval']#小于一年的更新频率，就拿10分
        self.info['updateScore']=min(1,max(updateScore,2))*10
        
        
        if self.__authorName__ is None:
            return 0, "Not a Github-based project!", self.info
        
        self.getIssueCount()
        
        self.sumCount=self.closeCount+self.openCount
        self.info['solveScore']=solveScore=self.closeCount/max(1,self.sumCount)*10
        
        
        hotScore=self.sumCount/1000
        self.info['hotScore']=min(1,max(hotScore,2))*10
        
         
        maintenanceScore=12-month_diff(self.getLastCommitTime())/2
        self.info['maintenanceScore']=min(10,max(maintenanceScore,2))
        
        self.info['recommendScore']=3*updateScore+2.5*solveScore+2*hotScore+2.5*maintenanceScore
        
        return 1, "ok", self.info
        
        
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
        issueLinkKey = None
        for key in projectUrls:
            if projectUrls[key].find("github.com") > 0:
                issueLinkKey = key
                break

        if issueLinkKey is not None:
            try:
                self.__authorName__, self.__repoName__ = githubUtils.extractAuthorAndRepoName(projectUrls[issueLinkKey])
            except:
                pass

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

        self.__cachedIssueCount__ =self.openCount, self.closeCount
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
    page = PypiPackageInfo("SpeechRecognition")
    print(page.getVersionList())
    print(page.getLastCommitTime())
    print(page.getIssueCount())
    

