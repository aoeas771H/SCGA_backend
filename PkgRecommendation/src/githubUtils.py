import datetime
import json

import requests

githubAuthToken = 'TOKEN'
if True:
    f = open("config.json")
    c = json.load(f)
    if "githubAuthToken" in c:
        githubAuthToken = c["githubAuthToken"]
    else:
        raise Exception("githubAuthToken not found in config.json")


def sendGithubRequest(path: str, queryString: 'dict|None' = None):
    headers = {
        'Authorization': 'Bearer ' + githubAuthToken,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    res = requests.get("https://api.github.com/" + path, headers=headers, params=queryString)
    return res.json()


def getLatestCommitTime(author: str, repo: str) -> 'datetime.datetime | None':
    path = 'repos/{}/{}/commits'.format(author, repo)
    obj = sendGithubRequest(path)
    if "message" in obj and obj['message'] == "Not Found":
        raise Exception("Github repo not found: author={},repo={}".format(author, repo))

    if not isinstance(obj, list):
        return None

    commit = obj[0]
    timeStr = commit['commit']['author']['date']
    ans = datetime.datetime.strptime(timeStr, '%Y-%m-%dT%H:%M:%SZ')
    return ans


def getIssueCount(author: str, repo: str, issueFilter: str):
    queryString = {
        "q": "repo:{}/{} type:issue {}".format(author, repo, issueFilter),
        "per_page": 1
    }
    obj = sendGithubRequest("search/issues", queryString)
    if "total_count" in obj:
        return obj["total_count"]
    else:
        return 0


class GithubRepo:
    # github issue界面的筛选表达式，前面的open或者close会自动加上
    githubIssueFilterSuffix = "error"

    def __init__(self, author, repo):
        self.__authorName__ = author
        self.__repoName__ = repo

        self.__cachedIssueCount__: 'tuple[int,int] | None' = None
        self.__cachedLastCommitTime__: 'datetime | None' = None

    def getIssueCount(self):
        """

        :return: 返回条件下的open,closed状态的issue数量
        """

        if self.__cachedIssueCount__ is not None:
            return self.__cachedIssueCount__

        if self.__authorName__ is None:
            raise Exception("Not a Github-based project!")

        openCount = getIssueCount(self.__authorName__, self.__repoName__,
                                  "is:open " + self.githubIssueFilterSuffix)
        closeCount = getIssueCount(self.__authorName__, self.__repoName__,
                                   "is:closed " + self.githubIssueFilterSuffix)

        self.__cachedIssueCount__ = openCount, closeCount
        return self.__cachedIssueCount__

    def getLastCommitTime(self):
        if self.__cachedLastCommitTime__ is not None:
            return self.__cachedLastCommitTime__

        if self.__authorName__ is None:
            raise Exception("Not a Github-based project!")

        self.__cachedLastCommitTime__ = getLatestCommitTime(self.__authorName__, self.__repoName__)
        return self.__cachedLastCommitTime__


if __name__ == '__main__':
    testRepo = GithubRepo("nodejs", "node")
    print(testRepo.getLastCommitTime())
    print(testRepo.getIssueCount())
