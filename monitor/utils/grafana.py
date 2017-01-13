# coding=utf-8
import json
from subprocess import Popen, PIPE

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
    pass


class SingleStat(Panel):
    def __init__(self, title, target):
        id = Panel.panel_id_counter
        Panel.panel_id_counter += 1
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
          "id": id,
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
          "postfix": "",
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
          "span": 2,
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

counter = 20
dashboard = Dashboard('autoDash')
for vm in ('74bc75b2-0b65-4eea-a943-add28d54d9a6',
           'f0bb0224-dab6-4531-bf63-94fe2d5b7686'):
    row = Row(vm)
    for meter in ('cpu_util', 'memory', 'memory.usage', 'disk.read.bytes.rate',
              'disk.write.bytes.rate', 'disk.capacity', 'disk.usage',
              'network.incoming.bytes.rate', 'network.outgoing.bytes.rate'):
        target = "Monitor.vm.%s.localhost.%s" % (vm, meter.replace('.', '_'))
        panel = SingleStat(title=meter, target=target)
        row.add_panel(panel._single_stat)
    dashboard.add_row(row._row)

print dashboard.sync()

