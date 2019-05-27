import os, sys, datetime, smtplib, json, config as cfg
from requests import post

lock = os.path.dirname(sys.argv[0]) + '/notif.txt'

if os.path.isfile(lock):
        file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getctime(lock))

        if file_age < datetime.timedelta(minutes=cfg.interval):
                sys.exit()

with open(lock, 'w+') as txt:
        txt.write('1')

def notif_email():
        server = False

        try:
                try:
                        server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)
                        server.starttls()
                        server.login(cfg.account, cfg.password)
                except:
                        if server:
                                server.quit()

                        server = smtplib.SMTP_SSL(cfg.smtp_server, cfg.port, timeout=10)
                        server.login(cfg.account, cfg.password)
        except:
                if server:
                        server.quit()

                server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)
                server.login(cfg.account, cfg.password)

        message = 'Subject: {}\n\n{}'.format(cfg.subject, cfg.message)
        server.sendmail(cfg.account, cfg.receiver, message)
        server.quit()

def notif_slack():
        slack_data = {
                'text': cfg.message,
                'username': cfg.slack_name,
                'icon_emoji': cfg.slack_icon
        }
        response = post(cfg.slack_wekbook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
        if response.status_code != 200 or response.text != 'ok':
                print('Failed to send slack notification, check slack_webhook_url.')

if cfg.notification_email:
        notif_email()

if cfg.notification_slack:
        notif_slack()
