FROM ubuntu:14.04

# localize
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN locale-gen zh_CN.UTF-8 &&\
  DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales
RUN locale-gen zh_CN.UTF-8  
ENV LANG zh_CN.UTF-8  
ENV LANGUAGE zh_CN:zh  
ENV LC_ALL zh_CN.UTF-8 

COPY install_nagios.sh /root/
RUN /bin/bash /root/install_nagios.sh

COPY install_graphite.sh /root/
RUN /bin/bash /root/install_graphite.sh

COPY install_grafana.sh /root/
RUN /bin/bash /root/install_grafana.sh

RUN apt-get install -y python-setuptools libmysqlclient-dev python-mysqldb vim && easy_install pip
 
COPY setup_monitor_config_system.sh /root/
RUN /bin/bash /root/setup_monitor_config_system.sh

COPY startup.sh /root/
CMD ["/bin/bash", "/root/startup.sh"]
