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
        self.versionList = None
        self.packageName = packageName
        self.__pypiJson__: 'dict | None' = None

        self.__authorName__: 'str | None' = None
        self.__repoName__: 'str | None' = None

        self.__cachedReleaseList__: 'list[ReleaseInfo] | None' = None
        self.__cachedIssueCount__: 'tuple[int,int] | None' = None
        self.__cachedLastCommitTime__: 'datetime | None' = None

    def getInfo(self):
        """
        return state, data(reason)
        
        """

        try:
            self.__loadJson__()
        except:
            return 0, "Network error or Package not found"

        self.versionList = self.getVersionList()

        if self.__authorName__ is None:
            return 0, "Not a Github-based project!"

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
            t = datetime.datetime.strptime(obj[-1]['upload_time_iso_8601'], '%Y-%m-%dT%H:%M:%S.%fZ')
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

        openCount = githubUtils.getIssueCount(self.__authorName__, self.__repoName__, "is:open " + self.githubIssueFilterSuffix)
        closeCount = githubUtils.getIssueCount(self.__authorName__, self.__repoName__, "is:closed " + self.githubIssueFilterSuffix)

        self.__cachedIssueCount__ = openCount, closeCount
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

    def getConflictScore(self) -> float:
        """
        计算包的推荐指数
        :return:
        """
        # TODO
        return 100.0


if __name__ == "__main__":
    page = PypiPackageInfo("xarray")
    page.getInfo()
    print(page.getVersionList())
    print(page.getLastCommitTime())
    print(page.getIssueCount())

