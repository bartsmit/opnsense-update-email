#!/usr/local/bin/python

###################################################################
# This script makes an API connection to OPNsense                 #
# and checks if there are any pending updates                     #
# if there are, it sends an email with details                    #
#                                                                 #
# Authors: Bart J. Smit, 'ObecalpEffect' and Franco Fichtner      #
#                                                                 #
# Version 1.2     07/05/2016                                      #
#                                                                 #
###################################################################

# import libraries
import json
import requests
import smtplib
from email.utils import formatdate

# define endpoint and credentials 
api_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
api_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
host = 'firewall.host.name'
recipients = 'your@email.address'
rcpt_name = 'Your Name'

url = 'https://' + host + '/api/core/firmware/status'
sender = 'root@' + host
message  = 'From: OPNsense Firewall <root@' + host + '>\r\n'
message += 'To: ' + rcpt_name + '<' + recipients + '>\r\n'
message += 'MIME-Version: 1.0\r\n'
message += 'Content-type: text/html\r\n'
message += 'Subject: Updates for OPNsense\r\n'
message += formatdate(localtime=True) + '\r\n'

# request data
r = requests.get(url,verify=True,auth=(api_key, api_secret))
if r.status_code == 200:
    response = json.loads(r.text)
    if response['status'] == 'ok':
        message += '<h2>Firewall Updates Available</h2>'
        message += '<br>The firewall has %s' % response['updates'] + ' update(s) available, totalling %s' % response['download_size'] + '<br>\r\n'
        nps = response['new_packages']
        if len(nps) > 0:
            message += '\r\n<br><b>New:</b><br>\r\n'
            if type(nps) == dict:
                for n in nps:
                    message += nps[n]['name'] + ' version ' + nps[n]['version'] + '<br>\r\n'
            else:
                for n in nps:
                    message += n['name'] + ' version ' + n['version'] + '<br>\r\n'
        ups = response['upgrade_packages']
        if len(ups) > 0:
            message += '\r\n<br><b>Upgrade:</b><br>\r\n'
            if type(ups) == dict:
                for u in ups:
                    message += ups[u]['name'] + ' from ' + ups[u]['current_version'] + ' to ' + ups[u]['new_version'] + '<br>\r\n'
            else:
                for u in ups:
                    message += u['name'] + ' from ' + u['current_version'] + ' to ' + u['new_version'] + '<br>\r\n'
        rps = response['reinstall_packages']
        if len(rps) > 0:
            message += '\r\n<br><b>Reinstall:</b><br>\r\n'
            if type(rps) == dict:
                for r in rps:
                    message += rps[r]['name'] + ' version ' + rps[r]['version'] + '<br>\r\n'
            else:
                for r in rps:
                    message += r['name'] + ' version ' + r['version'] + '<br>\r\n'
        message += '<br>Click <a href=\"https://' + host + '/ui/core/firmware/\">here</a> to fetch them.<br>\r\n'
        if response['upgrade_needs_reboot'] == '1':
            message += '<h3>This requires a reboot</h3>'
        s = smtplib.SMTP('localhost')
        s.sendmail(sender,recipients,message)
else:
    print ('Connection / Authentication issue, response received:')
    print r.text
