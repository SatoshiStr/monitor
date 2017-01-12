FROM ubuntu:14.04

ARG LOCAL_IP
# localize
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN locale-gen zh_CN.UTF-8 &&\
  DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales
RUN locale-gen zh_CN.UTF-8  
ENV LANG zh_CN.UTF-8  
ENV LANGUAGE zh_CN:zh  
ENV LC_ALL zh_CN.UTF-8 

# ganglia
COPY install_ganglia.sh /root/
RUN /bin/bash /root/install_ganglia.sh

# nagios
COPY install_nagios.sh /root/
RUN /bin/bash /root/install_nagios.sh
COPY commands.cfg /etc/nagios3/
COPY send_notify.py /usr/bin/
# check_ganglia
COPY check_ganglia /usr/lib/nagios/plugins/
RUN chmod a+x /usr/lib/nagios/plugins/check_ganglia
# check openstack vm
COPY openrc /openrc

COPY check_vm /usr/lib/nagios/plugins/
RUN chmod a+x /usr/lib/nagios/plugins/check_vm && chmod a+r /openrc && \
    mkdir -p /etc/nagios3/vm_cache/ && \
    chown nagios3:nagios3 /etc/nagios3/vm_cache/

COPY install_graphite.sh /root/
RUN /bin/bash /root/install_graphite.sh

COPY install_grafana.sh /root/
RUN /bin/bash /root/install_grafana.sh

# config system
RUN apt-get install -y python-setuptools libmysqlclient-dev python-mysqldb vim && easy_install pip
 
COPY setup_monitor_config_system.sh /root/
RUN /bin/bash /root/setup_monitor_config_system.sh

RUN apt-get install -y --force-yes software-properties-common && \
    add-apt-repository cloud-archive:mitaka -y && \
    apt-get update && \
    apt-get install -y python-ceilometerclient python-novaclient

COPY startup.sh /root/
CMD ["/bin/bash", "/root/startup.sh"]
