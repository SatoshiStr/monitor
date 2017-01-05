### 功能
- 添加主机，在主机上安装nrpe并修改配置
- 添加监控项目，修改nagios节点的配置（可能需要修改被监控节点的nrpe配置，也可以选择在nrpe安装时一次配完）


### 添加主机
添加主机到nagios中，分为两部
- 在主机部署nrpe，如果主机为nagios节点则不用
- 在nagios配置文件中添加主机的配置，并重启nagios服务

#### 主机状态
```
    (点击安装nrpe并配置)
新加入-------->配置中-------->已加入
  |                (配置完成)
  |-->配置失败
```
使用ansible进行安装并配置，成功后修改nagios配置  
使用后台队列运行ansible


### 添加监控项目
- 监控其他服务
    - mysql
    - libvirt
    - memcached
- openstack服务进程
- 虚拟机数目
- 虚拟机性能
    - 每台虚拟机的内存使用百分比
    - 虚拟机占用的主机RAM的大小
    - 虚拟机占用的磁盘空间大小
- 主机硬件
    - 内存
    - 磁盘
    - 网络

直接修改nagios配置

### gmond 指标
#### cpu
load_one  平均负荷
load_five
load_fifteen

cpu_idle cpu空闲 百分比
cpu_user user-level的cpu占用率 百分比
cpu_system

#### disk
disk_total 总磁盘空间 GB
disk_free 空闲

#### memory
mem_total 总内存空间 KB
mem_free
swap_total
swap_free

#### proc
proc_total 总进程数
proc_run 运行进程数

#### network
bytes_in 每秒收到的字节数 B/s
bytes_out

