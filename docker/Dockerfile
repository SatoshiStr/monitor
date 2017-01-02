FROM ubuntu:14.04

COPY install_nagios.sh /root/
RUN /bin/bash /root/install_nagios.sh

COPY install_graphite.sh /root/
RUN /bin/bash /root/install_graphite.sh

COPY install_grafana.sh /root/
RUN /bin/bash /root/install_grafana.sh

# copy monitor config system
COPY monitor /root/
COPY setup_monitor_config_system.sh /root/
RUN /bin/bash /root/setup_monitor_config_system.sh

COPY startup.sh /root/
CMD ["/bin/bash", "/root/startup.sh"]
