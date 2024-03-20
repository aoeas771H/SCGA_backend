import datetime
from typing import Tuple, Optional
import requests

# 有特殊含义的一级目录名不能作为author名
authorNameBlackList = ['downloads', 'sponsors']


def extractAuthorAndRepoName(url: str) -> tuple:
    """
    Extracts the author and name of a GitHub repository from a URL.

    Args:
    url (str): A string containing the URL of the GitHub repository.

    Returns:
    tuple: A tuple containing the author and name of the GitHub repository.
    """
    split_url = url.split('/')
    if split_url[2] != "github.com":
        raise Exception("Not a Github-based project!")

    author = split_url[3]
    repo_name = split_url[4]

    if author in authorNameBlackList:
        return None, None

    if repo_name.find("#") > 0:
        repo_name = repo_name.split("#")[0]

    if repo_name.find(".git") > 0:
        repo_name = repo_name.replace(".git", "")

    return author, repo_name


# 一次更新的信息
class ReleaseInfo:
    def __init__(self, versionName: str, versionTime: datetime.datetime):
        self.versionName = versionName
        self.versionTime = versionTime


# 输入一个pypi中有的包名，输出其最近几个版本的更新时间。藉由此，我们可以评估出这个包的更新频率
class PypiProject:
    # github issue界面的筛选表达式，前面的open或者close会自动加上
    githubIssueFilterSuffix = "error"

    def __init__(self, packageName: str):
        self.closeCount = None
        self.openCount = None
        self.packageName = packageName
        self.__pypiJson__: 'dict | None' = None

        self.__authorName__: 'str | None' = None
        self.__repoName__: 'str | None' = None
        self.__githubLink__: 'str | None' = None

        self.__cachedReleaseList__: 'list[ReleaseInfo] | None' = None
        self.__cachedIssueCount__: 'tuple[int,int] | None' = None
        self.__cachedLastCommitTime__: 'datetime | None' = None

    def loadJson(self):
        url = "https://pypi.org/pypi/{}/json".format(self.packageName)
        res = requests.get(url)
        self.__pypiJson__ = res.json()
        if 'info' not in self.__pypiJson__:
            if 'message' in self.__pypiJson__:
                raise Exception(self.__pypiJson__['message'])
            raise Exception('Package not found')

    def getVersionList(self):
        """

        :return: 返回该包每次发布的版本号与发布时间
        """
        if self.__cachedReleaseList__ is not None:
            return self.__cachedReleaseList__

        if self.__pypiJson__ is None:
            self.loadJson()

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

    def getGithubAuthorAndRepoName(self) -> Optional[Tuple[str, str]]:
        if self.__pypiJson__ is None:
            self.loadJson()

        if self.__authorName__ is not None:
            return self.__authorName__, self.__repoName__

        projectUrls = self.__pypiJson__['info']['project_urls']
        for key in projectUrls:
            if projectUrls[key].find("github.com") > 0:
                issueLinkKey = key
                self.__authorName__, self.__repoName__ = extractAuthorAndRepoName(projectUrls[issueLinkKey])
                if self.__authorName__ is not None:
                    break

        if self.__authorName__ is not None:
            return self.__authorName__, self.__repoName__
        else:
            raise Exception("Unable to find github link of package {} from pypi!".format(self.packageName))


if __name__ == "__main__":
    page = PypiProject("h5serv")
    print(page.getVersionList())
    print(page.getGithubAuthorAndRepoName())