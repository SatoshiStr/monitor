ceilometer是openstack的监控项目Telemeter的一部分，用于收集监控信息。  
ceilometer有3个主要的术语：
- meter 监控项目，包括虚拟机和主机的各种信息，具体看
http://docs.openstack.org/admin-guide/telemetry-measurements.html
。通过配置pipelines增加要监控的项目。
- sample 采样，默认设置为10分钟对监控的项目进行1次采样，可以通过`celiometer sample-list`
获取采样数据。如`ceilometer sample-list -m cpu_util -q 
'resource_id=b7fc623d-1d4a-4ac7-b96b-78c9d921fa74;timestamp>2013-05-21T03:18:20;timestamp<2013-05-21T03:30:20'`
可以获取某个资源在一个时间段内的所有采样数据。也可以通过python的sdk获取。获取后的采样可以
在web页面进行可视化处理。
- statistics
一段时间内的统计，包括最大最小平均值。可以与图表搭配使用。


### 监控项目
#### 主机
磁盘空间使用率
磁盘io使用率
CPU 使用率
内存使用率
网卡使用率


使用的Openstack Services 包括 Keystone Nova Glance Neutron Telemeter
http://www.aboutyun.com/thread-12408-1-1.html
