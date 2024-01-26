from abc import ABC, abstractmethod

import requests
import parsel
import datetime


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
    # github issue界面的筛选表达式
    githubIssueFilter = "is:issue is:open error"

    def __init__(self, packageName: str):
        self.packageName = packageName
        self.__pypiHtml__: 'str | None' = None
        self.__githubHtml__: 'str | None' = None
        self.__pypiSelector__: 'parsel.selector.Selector | None' = None
        self.__githubSelector__: 'parsel.selector.Selector | None' = None
        self.__githubIssueLink__: 'str | None' = None

        self.__cachedReleaseList__: 'list[ReleaseInfo] | None' = None
        self.__cachedIssueCount__: 'tuple[int,int] | None' = None

    def __loadHtml__(self):
        url = "https://pypi.org/project/{}/".format(self.packageName)
        res = requests.get(url)
        self.__pypiHtml__ = res.text
        self.__pypiSelector__ = parsel.Selector(self.__pypiHtml__)

        for sidebar in self.__pypiSelector__.css(".sidebar-section"):
            title = sidebar.css(".sidebar-section__title::text").get()
            if title is None:
                continue
            if title.strip() != "Project links":
                continue

            for link in sidebar.css(".vertical-tabs__tab"):
                lineName = link.xpath(".//text()[2]").get().strip()
                if lineName == "Issue Tracker":
                    self.__githubIssueLink__ = link.xpath(".//@href").get()
                    break

    def __loadGithubIssuePage__(self):
        if self.__pypiSelector__ is None:
            self.__loadHtml__()

        if self.__githubIssueLink__ is None:
            raise Exception("Issue tracker not found!")

        if self.__githubIssueLink__.find("github.com") == -1:
            raise Exception("Not a github project!")

        res = requests.get(self.__githubIssueLink__, params={'q': self.githubIssueFilter})
        self.__githubHtml__ = res.text
        self.__githubSelector__ = parsel.Selector(self.__githubHtml__)

    def getVersionList(self):
        """

        :return: 返回该包每次发布的版本号与发布时间
        """
        if self.__cachedReleaseList__ is not None:
            return self.__cachedReleaseList__

        if self.__pypiSelector__ is None:
            self.__loadHtml__()

        ans: 'list[ReleaseInfo]' = []
        for htmlRelease in self.__pypiSelector__.css(".release-timeline>.release"):
            versionName = htmlRelease.css(".release__version::text").get().strip()
            releaseTimeStr = htmlRelease.css(".release__version-date>time").xpath('.//@datetime').get()
            t = datetime.datetime.strptime(releaseTimeStr, '%Y-%m-%dT%H:%M:%S%z')
            ans.append(ReleaseInfo(versionName, t))

        self.__cachedReleaseList__ = ans
        return ans

    def getIssueCount(self):
        """

        :return: 返回条件下的open,closed状态的issue数量
        """
        try:
            if self.__cachedIssueCount__ is not None:
                return self.__cachedIssueCount__

            if self.__githubSelector__ is None:
                self.__loadGithubIssuePage__()

            toolbar = self.__githubSelector__.css("#js-issues-toolbar")
            openHtml = toolbar.css('a[data-ga-click="Issues, Table state, Open"]')
            if openHtml is None:
                raise Exception("Failed to get github issue count")

            openText = openHtml.xpath(".//text()").getall()[3].strip()
            openCount = int(openText[0:-5])
            closedHtml = toolbar.css('a[data-ga-click="Issues, Table state, Closed"]').xpath(".//text()") \
                .getall()[3].strip()
            closeCount = int(closedHtml[0:-7])

            self.__cachedIssueCount__ = openCount, closeCount
            return self.__cachedIssueCount__
        except:
            return 0,0

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
    print(page.getVersionList())
