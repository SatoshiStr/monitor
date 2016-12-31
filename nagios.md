### 安装
```
sudo apt-get install -y apache2
sudo apt-get install -y mysql-server mysql-client
sudo apt-get install -y php5 php5-mysql libapache2-mod-php5
sudo apt-get install -y phpmyadmin
```
```
sudo apt-get install nagios3 nagios-nrpe-plugin -y
```

###
#### 主机和服务
#### 插件
NRPE nagios remote plugin executor  
包括在本地执行的check_nrpe的插件，以及远程的守护进程


### 对象
包括 主机、服务、主机组、服务组、主机依赖、联系人、联系人组、命令等

##### /etc/nagios3/nagios.cfg
```
cfg_dir=xxx 对象配置文件夹
```


