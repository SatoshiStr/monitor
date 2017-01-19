# coding=utf-8
import json
from subprocess import Popen, PIPE
from app.models import Machine, Group

MONITOR_IP = '127.0.0.1'
GRAFANA_USER = 'admin'
GRAFANA_PASS = 'admin'
GRAFANA_URL = 'http://%s:%s@%s:3000' % (GRAFANA_USER, GRAFANA_USER, MONITOR_IP)

null = None
false = False
true = True


def run_command(command):
    if isinstance(command, str) or isinstance(command, unicode):
        command = command.split()
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout = proc.stdout.read()
    return stdout


def get_data(path):
    command = 'curl ' + GRAFANA_URL + path
    return json.loads(run_command(command))


def post_json(path, data):
    command = 'curl -X POST -H '.split()
    command.append("Content-Type: application/json")
    command.append('-d')
    command.append(json.dumps(data))
    command.append(GRAFANA_URL+path)
    return json.loads(run_command(command))


def init_data_source():
    data = {
        "name": "monitor",
        "type": "graphite",
        "url": "http://%s:8008" % MONITOR_IP,
        "access": "proxy",
        "basicAuth": False
    }
    return post_json('/api/datasources', data)


class Dashboard(object):
    def __init__(self, title):
        self._dashboard = {
            "annotations": {
                "list": []
            },
            "editable": true,
            "gnetId": null,
            "graphTooltip": 0,
            "hideControls": false,
            "id": null,
            "links": [],
            "rows": [],
            "schemaVersion": 14,
            "style": "light",
            "tags": [],
            "templating": {
                "enable": true,
                "list": []
            },
            "time": {
                "from": "now-6h",
                "to": "now"
            },
            "timepicker": {
                "refresh_intervals": [],
                "time_options": []
            },
            "timezone": "browser",
            "title": title,
            "version": 2
        }

    def add_custom_template(self, name, options):
        item = {
            "allValue": None,
            "current": {
                "tags": [],
                "text": "All",
                "value": [
                    "$__all"
                ]
            },
            "hide": 0,
            "includeAll": True,
            "label": None,
            "multi": True,
            "name": name,
            "options": [
                {
                    "selected": True,
                    "text": "All",
                    "value": "$__all"
                }
            ],
            "query": "",
            "type": "custom"
        }
        opts = []
        query = []
        for opt in options:
            if isinstance(opt, str):
                value = opt
                text = opt
            else:
                value, text = opt
            opts.append({
                "selected": False,
                "text": text,
                "value": value
            })
            query.append(value)
        item['options'] += opts
        item['query'] = ','.join(query)
        self._dashboard['templating']['list'].append(item)

    def add_row(self, row):
        self._dashboard['rows'].append(row)

    def sync(self):
        framework = {
            "dashboard": self._dashboard,
            "overwrite": True
        }
        return post_json('/api/dashboards/db', framework)


class Row(object):
    def __init__(self, title, show_title=True, repeat=None, height=130):
        self._row = {
            "collapse": false,
            "height": height,
            "panels": [],
            "repeat": "vm",
            "repeatIteration": null,
            "repeatRowId": null,
            "showTitle": show_title,
            "title": title,
            "titleSize": "h6"
        }

    def add_panel(self, panel):
        self._row['panels'].append(panel)


class Panel(object):
    panel_id_counter = 1
    def __init__(self):
        self.id = Panel.panel_id_counter
        Panel.panel_id_counter += 1


class SingleStat(Panel):
    def __init__(self, title, target, span=3, postfix=''):
        super(SingleStat, self).__init__()
        self._single_stat = {
          "cacheTimeout": null,
          "colorBackground": false,
          "colorValue": false,
          "colors": [
            "rgba(245, 54, 54, 0.9)",
            "rgba(237, 129, 40, 0.89)",
            "rgba(50, 172, 45, 0.97)"
          ],
          "datasource": "monitor",
          "format": "none",
          "gauge": {
            "maxValue": 100,
            "minValue": 0,
            "show": false,
            "thresholdLabels": false,
            "thresholdMarkers": true
          },
          "id": self.id,
          "interval": null,
          "links": [],
          "mappingType": 1,
          "mappingTypes": [
            {
              "name": "value to text",
              "value": 1
            },
            {
              "name": "range to text",
              "value": 2
            }
          ],
          "maxDataPoints": 100,
          "nullPointMode": "connected",
          "nullText": null,
          "postfix": postfix,
          "postfixFontSize": "50%",
          "prefix": "",
          "prefixFontSize": "50%",
          "rangeMaps": [
            {
              "from": "null",
              "text": "N/A",
              "to": "null"
            }
          ],
          "span": span,
          "sparkline": {
            "fillColor": "rgba(31, 118, 189, 0.18)",
            "full": false,
            "lineColor": "rgb(31, 120, 193)",
            "show": false
          },
          "targets": [
            {
              "refId": "A",
              "target": target
            }
          ],
          "thresholds": "",
          "title": title,
          "type": "singlestat",
          "valueFontSize": "80%",
          "valueMaps": [
            {
              "op": "=",
              "text": "N/A",
              "value": "null"
            }
          ],
          "valueName": "avg"
        }


class Graph(Panel):
    def __init__(self, title, target, span=12, unit='short'):
        super(Graph, self).__init__()
        self._graph = {
          "aliasColors": {},
          "bars": false,
          "datasource": "monitor",
          "fill": 1,
          "id": self.id,
          "legend": {
            "avg": false,
            "current": false,
            "max": false,
            "min": false,
            "show": true,
            "total": false,
            "values": false
          },
          "lines": true,
          "linewidth": 1,
          "nullPointMode": "null",
          "percentage": false,
          "pointradius": 5,
          "points": false,
          "renderer": "flot",
          "seriesOverrides": [],
          "span": span,
          "stack": false,
          "steppedLine": false,
          "targets": [
            {
              "refId": "A",
              "target": target
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeShift": null,
          "title": title,
          "tooltip": {
            "shared": true,
            "sort": 0,
            "value_type": "individual"
          },
          "type": "graph",
          "xaxis": {
            "mode": "time",
            "name": null,
            "show": true,
            "values": []
          },
          "yaxes": [
            {
              "format": unit,
              "label": null,
              "logBase": 1,
              "max": null,
              "min": null,
              "show": true
            },
            {
              "format": "short",
              "label": null,
              "logBase": 1,
              "max": null,
              "min": null,
              "show": true
            }
          ]
        }


def create_stat_list(title, machines):
    local_host = 'localhost'
    dashboard = Dashboard(title)
    for machine in machines:
        row = Row(machine.hostname if machine.type == 'Host' else machine.vm_id)
        for service in machine.get_services():
            if machine.type == 'Host':
                meter = service.command.split('!')[1]
                target = 'scale(Monitor.host.%s.%s, %f)' % \
                         (machine.hostname, meter, service.rate)
            else:
                meter = service.command.split('!')[2].replace('.', '_')
                target = 'scale(Monitor.vm.%s.%s.%s, %f)' % \
                         (machine.vm_id, local_host, meter, service.rate)
            panel = SingleStat(title=meter, target=target, span=2,
                               postfix=service.unit)
            row.add_panel(panel._single_stat)
        dashboard.add_row(row._row)
    result = dashboard.sync()
    return result


def create_detail_graph(machine):
    local_host = 'localhost'
    if machine.type == 'Host':
        title = u'主机-' + machine.hostname
    else:
        title = u'VM-' + machine.vm_id
    dashboard = Dashboard(title)
    row = Row(title, height=350)
    for service in machine.get_services():
        if machine.type == 'Host':
            meter = service.command.split('!')[1]
            target = 'Monitor.host.%s.%s' % (machine.hostname, meter)
        else:
            meter = service.command.split('!')[2].replace('.', '_')
            target = 'Monitor.vm.%s.%s.%s' % (machine.vm_id, local_host,
                                              meter)
        panel = Graph(title=meter, target=target, span=6,
                      unit=service.graph_unit)
        row.add_panel(panel._graph)
    dashboard.add_row(row._row)
    return dashboard.sync()


def sync_all():
    # 为每个group、全部vm、全部host创建single-stat列表仪表盘
    all_hosts = Machine.query.filter_by(type='Host').all()
    create_stat_list(u'全部主机', all_hosts)
    all_vms = Machine.query.filter_by(type='VM').all()
    create_stat_list(u'全部VM', all_vms)
    host_groups = Group.query.filter_by(type='Host').all()
    for group in host_groups:
        create_stat_list(u'主机组-%s' % group.name, group.machines)
    vm_groups = Group.query.filter_by(type='VM').all()
    for group in vm_groups:
        create_stat_list(u'VM组-%s' % group.name, group.machines)
    # 为每台vm、host创建graph详细仪表板
    for host in all_hosts:
        create_detail_graph(host)
    for vm in all_vms:
        create_detail_graph(vm)
