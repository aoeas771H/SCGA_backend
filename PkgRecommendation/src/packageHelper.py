import datetime
import numpy as np

from src.githubUtils import GithubRepo
from src.pypiUtils import PypiProject
from src.gptUtils import GPTClient

def month_diff(target_date):
    # print(target_date)
    current_date = datetime.datetime.now()
    year_diff = current_date.year - target_date.year
    month_diff = current_date.month - target_date.month

    total_months = year_diff * 12 + month_diff
    return total_months


class PackageInfo:

    def __init__(self, packageName: str):
        self.packageName = packageName
        self.pypiProject: 'PypiProject' = PypiProject(packageName)
        self.githubRepo: 'GithubRepo | None' = None

    def getInfo(self):
        """
        return state, reason, data
        
        """
        print(self.packageName + "syffffffffff")
        self.info = {}
        self.info['gpt'] = None
        self.info['recommendScore'] = None
        try:
            self.pypiProject.loadJson()
        except:
            return 0, "Network error or Package not found", self.info

        self.info['versionList'] = self.pypiProject.getVersionList()

        self.info['averageUpdateInterval'] = self.getAverageUpdateInterval()

        updateScore = 180 / self.info['averageUpdateInterval']  # 小于一年的更新频率，就拿10分
        self.info['updateScore'] = updateScore = min(1, max(updateScore, 0.2)) * 10

        # bamboo
        """
        bamboo
        pyxhook
        PytorchNLP
        mistune
        drone
        mars
        """

        try:
            self.githubRepo = GithubRepo(*self.pypiProject.getGithubAuthorAndRepoName())
        except Exception as e:
            print(e)
            pass

        if self.githubRepo is None:
            return 0, "Not a Github-based project!", self.info

        openCount, closeCount = self.githubRepo.getIssueCount()

        sumCount = closeCount + openCount
        lastCommitTime = self.githubRepo.getLastCommitTime()

        solveScore = closeCount / max(1, sumCount) * 10
        self.info['solveScore'] = solveScore

        hotScore = np.sqrt(sumCount / 10)
        self.info['hotScore'] = hotScore = min(10, max(hotScore, 2))


        maintenanceScore = 9 - month_diff(lastCommitTime) / 2

        self.info['maintenanceScore'] = maintenanceScore = min(10, max(maintenanceScore, 2))

        self.info['recommendScore'] = 3 * updateScore + 2.5 * solveScore + 2 * hotScore + 2.5 * maintenanceScore


        gptClient = GPTClient()
        self.info['gpt'] = gptClient.getResponse(self.info['averageUpdateInterval'], openCount, closeCount, lastCommitTime)

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
