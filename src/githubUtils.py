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

    if repo_name.find("#") > 0:
        repo_name = repo_name.split("#")[0]

    if repo_name.find(".git") > 0:
        repo_name = repo_name.replace(".git", "")

    return author, repo_name


if __name__ == '__main__':
    print(getLatestCommitTime("nodejs", "node"))
    print(getIssueCount("nodejs", "node", "state:closed"))
