# PS
Linux服务器下部署项目
这里只采用了anaconda加gunicorn加flask的最基本的部署，保证前端能访问到后端即可，并没有做诸如负载均衡等操作。

## anaconda安装
参考网上安装方法即可：https://blog.csdn.net/wyf2017/article/details/118676765

官网下载.sh文件，有点大（1.4G左右）
安装完成之后source activate name启动虚拟环境名称

## gunicorn安装
类似windows上使用anaconda，建立虚拟环境，安装项目所需要的第三方包。

除此之外，需要安装gunicorn
```
pip install gunicorn
```
安装完之后在你的项目目录下运行
```
nohup python -m gunicorn -w 4 -b 0.0.0.0:27779 --timeout 70 main:app > app.log 2>&1
```

- main:项目的入口文件名
- app:flask框架下声明的应用名：例如代码当中：app = Flask(__name__)
- -w 4:表示以4个进程运行这个程序
- -b 0.0.0.0:27779:表示将flask api的端口映射到服务器的27779端口。注：一定记得检查服务器防火墙和安全组对应端口开放没！！！
- --timeout 70:设定访问超时时间为70秒，可选
- app.log 2>&1: 将控制台输出信息重定向到app.log，推荐设置，方便查找bug
- 更多参数可百度使用即可

如果想关闭当前这个进程，查看app.log文件
```
[2024-02-27 12:35:41 +0800] [1303] [INFO] Starting gunicorn 21.2.0
[2024-02-27 12:35:41 +0800] [1303] [INFO] Listening at: http://0.0.0.0:27779 (1303)
[2024-02-27 12:35:41 +0800] [1303] [INFO] Using worker: sync
[2024-02-27 12:35:41 +0800] [1306] [INFO] Booting worker with pid: 1306
[2024-02-27 12:35:41 +0800] [1307] [INFO] Booting worker with pid: 1307
[2024-02-27 12:35:41 +0800] [1308] [INFO] Booting worker with pid: 1308
[2024-02-27 12:35:41 +0800] [1309] [INFO] Booting worker with pid: 1309
```
关掉对应进程(kill)即可