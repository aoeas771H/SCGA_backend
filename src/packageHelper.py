from abc import ABC, abstractmethod

import requests
import datetime
import githubUtils
 

class IPackageInfo(ABC):
    @abstractmethod
    def getConflictScore(self) -> float:
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

    def __loadJson__(self):
        url = "https://pypi.org/pypi/{}/json".format(self.packageName)
 
        res = requests.get(url)
        self.__pypiJson__ = res.json()
        if 'info' not in self.__pypiJson__:
            if 'message' in self.__pypiJson__:
                raise Exception(self.__pypiJson__['message'])
            raise Exception('Package not found')

        targetDict = self.__pypiJson__['info']['project_urls']
        self.githubFlag=0
        for val in targetDict.values():
            if "github.com" in val:
                Link=val
                self.githubFlag=1
                break
        if(self.githubFlag):
            self.__authorName__, self.__repoName__ = githubUtils.extractAuthorAndRepoName( Link)
        else:
            print("this package, no github respository")

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
            #print(obj)
            t = datetime.datetime.strptime(obj[-1]['upload_time_iso_8601'], '%Y-%m-%dT%H:%M:%S.%fZ')
            ans.append(ReleaseInfo(versionName, t))

        self.__cachedReleaseList__ = ans
        return ans
    
    def getAverageUpdateInterval(self):
        """
        计算并返回平均更新间隔（以天为单位）。
        """
        try:
            version_list = self.getVersionList()
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
                return None

            # 计算平均间隔
            average_interval = sum(intervals) / len(intervals)
            return average_interval
        except:
            return "N/A"

    def getIssueCount(self):
        """

        :return: 返回条件下的open,closed状态的issue数量
        """
        try:
            if self.__pypiJson__ is None:
                self.__loadJson__()

            if self.__cachedIssueCount__ is not None:
                return self.__cachedIssueCount__

            openCount = githubUtils.getIssueCount(self.__authorName__, self.__repoName__, "is:open " + self.githubIssueFilterSuffix)
            closeCount = githubUtils.getIssueCount(self.__authorName__, self.__repoName__, "is:closed " + self.githubIssueFilterSuffix)

            self.__cachedIssueCount__ = openCount+closeCount
            return self.__cachedIssueCount__
        except:
            return "N/A"

    def getLastCommitTime(self):
        try:
            if self.__pypiJson__ is None:
                self.__loadJson__()

            if self.__cachedLastCommitTime__ is not None:
                return self.__cachedLastCommitTime__

            ans = githubUtils.getLatestCommitTime(self.__authorName__, self.__repoName__)
            return month_diff(ans)
        except:
            return "N/A"
        # if self.__pypiJson__ is None:
        #     self.__loadJson__()

        # if self.__cachedLastCommitTime__ is not None:
        #     return self.__cachedLastCommitTime__

        # ans = githubUtils.getLatestCommitTime(self.__authorName__, self.__repoName__)
        # return month_diff(ans)

    def getConflictScore(self) -> float:
        """
        怎么计算包的冲突指数？
        :return:
        """
        # TODO
        return 100.0
    
def month_diff(target_date):
    current_date = datetime.datetime.now()
    year_diff = current_date.year - target_date.year
    month_diff = current_date.month - target_date.month

    total_months = year_diff * 12 + month_diff
    return total_months

if __name__ == "__main__":
    page = PypiPackageInfo("grab")
    print(page.getIssueCount())
    print(page.getLastCommitTime())
    #print(page.getVersionList())
    print(page.getAverageUpdateInterval())
