# coding=utf-8
import urllib2
import json
import sys
# arg1 subject
# arg2 recipient
# arg3 content

headers = {'Content-Type': 'application/json'}
data = {
    'subject': sys.argv[1],
    'recipient': sys.argv[2],
    'content': sys.argv[3],
}
request = urllib2.Request(url='http://localhost:5000/alarm/add', headers=headers, data=json.dumps(data))
response = urllib2.urlopen(request)
