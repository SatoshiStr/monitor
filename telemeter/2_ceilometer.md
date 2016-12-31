### 术语
- metering 计量
- meter 计量项目
- sample 采样
- statistics 一段时间内的统计，包括最大最小平均

#### meter
`ceilometer meter-list`   
类型：
- cumulative
- delta
- gauge

#### sample
`ceilometer sample-list -m cpu_util`
`ceilometer sample-list -m cpu_util -q 
'resource_id=b7fc623d-1d4a-4ac7-b96b-78c9d921fa74;timestamp>2013-05-21T03:18:20;timestamp<2013-05-21T03:30:20'`
包括采样的值和时间

#### statistics

### 修改pipe
```
service ceilometer-agent-central restart
service ceilometer-agent-compute restart
service ceilometer-agent-notification restart
service ceilometer-api restart
service ceilometer-collector restart
```

### snmp 配置
```
apt-get install -y snmp snmpd

agentAddress udp:127.0.0.1:161
改为 
agentAddress udp:161,udp6:[::1]:161

添加 view   systemonly  included   .1   80

重启，运行snmpwalk -v 2c -c public localhost
```
pipelines配置
```
sources:  # 在sources段下增加如下配置：
    - name: hardware_source
      interval: 600
      meters:
          - "hardware.*"
      resources:
          - snmp://192.168.0.100  # 被监控的物理机snmpd服务ip，可以同时加入多行，表示同时监控多个物理机
          - snmp://192.168.0.101
      sinks:
          - meter_sink
```
