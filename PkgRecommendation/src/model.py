import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np
# 读取Excel文件
file_path = 'synk_info.xlsx'  # 修改为你的Excel文件路径
df = pd.read_excel(file_path)

# # 假设你的列名已经正确匹配
# X = df[['averageUpdateInterval','solveRate','sumCount','monthAway']]
# y = df['synkScore']

# # 分割数据为训练集和测试集
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # 使用随机森林回归模型
# regressor = RandomForestRegressor(n_estimators=10000, random_state=42)
# regressor.fit(X_train, y_train)

# # 进行预测
# y_pred = regressor.predict(X_test)

# # 评估模型
# print("均方误差(MSE):", mean_squared_error(y_test, y_pred))
# print("R2 分数:", r2_score(y_test, y_pred))

# # 可视化真实值与预测值
# plt.scatter(y_test, y_pred)
# plt.xlabel('true value')
# plt.ylabel('predicted value')
# plt.title('true value vs predicted value')
# plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--')
# plt.show()

# # 特征重要性
# feature_importances = pd.Series(regressor.feature_importances_, index=X.columns)
# feature_importances.plot(kind='barh')
# plt.title('Feature Importances')
# plt.show()
def gaussian(x, mean, sigma, amplitude):
    return amplitude * np.exp(-((x - mean)**2 / (2 * sigma**2)))
#xnames=['averageUpdateInterval','solveRate','sumCount','monthAway']
xnames=['monthAway']
label=['low-healthy','medium-healthy','high-healthy']
colors=['red','green','blue']
for xname in xnames:
    x_data = df[xname]
    # 获取x_data排序后的索引
    sorted_indices = np.argsort(x_data)
 
    # 使用索引来排序x_data和y_data
    x_data = x_data[sorted_indices]
    
    #plt.scatter(x_data, y_data, label='ori data')
     
    for i in range(3):
        y_data = df["synkScore"]
        y_data = y_data[sorted_indices]

        y_data=y_data.apply(lambda x: 0.8 if i*35 <= x < i*35+35 else 0)

        # 使用curve_fit拟合高斯函数
        initial_guess = [0, 10, 1]  # 初始猜测：mean=0, sigma=1, amplitude=1
        params, covariance = curve_fit(gaussian, x_data, y_data, p0=initial_guess,maxfev=10000000)
        
        print(params)
       

        # 拟合的参数
        mean_fitted, sigma_fitted, amplitude_fitted = params

        # 绘制原始数据和拟合曲线
        
        plt.plot(x_data, gaussian(x_data, mean_fitted, sigma_fitted, amplitude_fitted), label=label[i], color=colors[i])
        plt.legend()
    plt.show()