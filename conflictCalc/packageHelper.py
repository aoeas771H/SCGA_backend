from abc import ABC, abstractmethod

import requests
import datetime
import githubUtils

def is_last_part_issues(url):
    # 使用 rsplit 方法从右侧分割字符串一次，获取最后一个 '/' 后的部分
    parts = url.rsplit('/', 1)
    if len(parts) == 2:  # 确保存在 '/' 分割的部分
        return parts[1].lower() == 'issues'  # 比较是否等于 'issue'，忽略大小写
    return False

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
        for val in targetDict.values():
            if is_last_part_issues(val):
                issueLink=val
                break
        print(issueLink)
        self.__authorName__, self.__repoName__ = githubUtils.extractAuthorAndRepoName(issueLink)

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

        openCount = githubUtils.getIssueCount(self.__authorName__, self.__repoName__, "is:open " + self.githubIssueFilterSuffix)
        closeCount = githubUtils.getIssueCount(self.__authorName__, self.__repoName__, "is:closed " + self.githubIssueFilterSuffix)

        self.__cachedIssueCount__ = openCount, closeCount
        return self.__cachedIssueCount__

    def getLastCommitTime(self):
        if self.__pypiJson__ is None:
            self.__loadJson__()

        if self.__cachedLastCommitTime__ is not None:
            return self.__cachedLastCommitTime__

        ans = githubUtils.getLatestCommitTime(self.__authorName__, self.__repoName__)
        return ans

    def getConflictScore(self) -> float:
        """
        怎么计算包的冲突指数？
        :return:
        """
        # TODO
        return 100.0


if __name__ == "__main__":
    page = PypiPackageInfo("flask")
    print(page.getIssueCount())
    print(page.getLastCommitTime())
    print(page.getVersionList())
