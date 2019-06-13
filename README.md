# IOPS-Challenge-2019
这个仓库是[iops.ai](http://iops.ai/)挑战赛2019，多维监测指标的异常定位，决赛运行环境。

- [x] 评测程序的基本实现：`run.py`
- [x] 基本的选手程序样例：`example_user/`
- [ ] 测试
    - [ ] 选手程序超时：忽略该条结果
    - [ ] 选手程序错误的输出：忽略错误输出，只识别符合格式的输出
    - [ ] 选手程序崩溃：只计算崩溃前输出的结果
     
## 选手需要准备的内容：
一个Docker镜像，其中包含了选手的程序和所有需要的环境。
请将docker镜像通过`docker save ${IMAGE} -o ${队名}.tar`命令保存在虚拟机的`/srv`目录下([docker save命令](https://docs.docker.com/engine/reference/commandline/save/))。
- Docker镜像的名字请设定为队名，和tar文件的名字也需一致
- 请保证镜像有正确的entrypoint
- 可以参考example_user中的写法
- 请自行利用`run.py`测试，确保符合规范。决赛过程中出现问题后果自负。

##  选手程序需要做什么
1. docker container内`/data`路径中，会按时序出现各个时间点的数据。格式和预赛相同，每个时间点对应的数据文件名为`{timestamp}.csv`（例如`1536827700.csv`）。
2. 监控程序会**定时**向选手程序的stdin写入一行并换行，内容为发生异常的时间戳。此时`/data`路径下保证会有此时刻及之前的所有时间点的数据。
3. 选手程序需要在接受到stdin输入的限定时间（**1min**）内输出根因结果。内容为一行，格式和预赛提交格式相同：`{timestamp},{root_cause string}`（例如`1501475700,a1&b2;a3&b4`）。注意需要**换行**和**刷新缓冲区**,不要加额外的空格，换行符是linux标准。超时的输出会被忽略。
不要在stdout中输出额外的内容，监控程序依赖系统提供的文件变化的时间读取内容

## 监控程序会做什么
1. 保证`/data`中按时间顺序依次出现各个时间点的数据。
2. 在异常数据到来的时候，向选手程序的stdin写入一行，内容为发生异常的时间戳。
3. 接受选手程序输出的按规定格式的根因结果。只有在后续时间点数据出现之前的结果才有效，否则会被直接忽略。
4. 每个选手程序拥有的计算资源
8 Cores，64GB RAM，200GB Storage
选手的Docker镜像将会通过以下参数启动Container：
``` bash
docker run -i --cpu=<cpu-limit> --memory=<memory-limit> --storage-opt size=<storage-limit> -v <data-path>:/data --ipc=private <container-name>
```


## 使用方法
1. 安装pipenv，参考[https://github.com/pypa/pipenv](https://github.com/pypa/pipenv)
2. 安装依赖环境
``` bash
pipenv install --python $(which python)
```
3. 进入虚拟环境
``` bash
pipenv shell
```
4. 执行
``` bash
python run.py
```

``` bash
python run.py --help
Usage: run.py [OPTIONS]

Options:
  --team TEXT           team name without any special characters  [required]
  --ground-truth PATH   path to ground truth file
  --data PATH           KPI data path
  --docker PATH         docker images parent path
  --cpu-limit INTEGER   client docker cpu limit
  --memory-limit TEXT   client docker memory limit
  --storage-limit TEXT  client docker storage limit
  --interval INTEGER    interval between every two points in seconds
  --log PATH            log file parent path
  --help                Show this message and exit.
```

以下是运行`example_user`的样例:
```bash
cd example_user
bash build_docker.sh
cd ..
python run.py --team example_user --ground-truth unittest_files/ground_truth.csv --data unittest_files/data/ --interval 2
```
输出的F1-score应当为1.0