# IOPS-Challenge-2019
这个仓库是[iops.ai](http://iops.ai/)挑战赛2019，多维监测指标的异常定位，决赛运行环境。

## 选手需要准备的内容：
一个Docker镜像，其中包含了选手的程序和所有需要的环境。
请将docker镜像通过`docker save ${IMAGE} -o ${队名}.tar`命令保存在虚拟机的`/srv`目录下([docker save命令](https://docs.docker.com/engine/reference/commandline/save/))。
请保证镜像有正确的entrypoint

##  选手程序需要做什么
1. docker container内`/data`路径中，会按时序出现各个时间点的数据。格式和预赛相同，每个时间点对应的数据文件名为`{timestamp}.csv`（例如`1536827700.csv`）。
2. 监控程序会**定时**向选手程序的stdin写入一行并换行，内容为发生异常的时间戳。此时`/data`路径下保证会有此时刻及之前的所有时间点的数据。
3. 选手程序需要在接受到stdin输入的限定时间（**1min**）内输出根因结果。内容为一行，格式和预赛提交格式相同：`{timestamp},{root_cause string}`（例如`1501475700,a1&b2;a3&b4`）。注意需要**换行**和**刷新缓冲区**。超时的输出会被忽略。

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
