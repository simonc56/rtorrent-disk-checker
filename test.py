# -*- coding: utf-8 -*-

from datetime import datetime

start = datetime.now()

import sys, os, smtplib, json, config as cfg
from subprocess import check_output
from remotecaller import xmlrpc
try:
        from urllib2 import Request, urlopen
except:
        from urllib.request import Request, urlopen

try:
        from torrents import completed
        from mountpoints import mount_points
except:
        print('Building cache. Please wait...')
        import cacher

        try:
                cacher.build_cache('test')
        except:
                print('Failed\nRun the script with its full path like:\npython /path/to/test.py 69')
                sys.exit()

        print('Cache built.')

def disk_usage(path):
        try:
                used_k = int(check_output(['du','-ks', path]).split()[0])
        except:
                used_k = 0
        return 1024 * used_k

def send_email():
        server = False

        try:
                try:
                        try:
                                print('\nAttempting to email using TLS\n')
                                server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)
                                server.starttls()
                                server.login(cfg.account, cfg.password)
                        except Exception as e:
                                print('Failed\n\nTLS Related Error:\n')
                                print(e)
                                print('\nAttempting to email using SSL\n')

                                if server:
                                        server.quit()

                                server = smtplib.SMTP_SSL(cfg.smtp_server, cfg.port, timeout=10)
                                server.login(cfg.account, cfg.password)
                except Exception as e:
                        print('Failed\n\nSSL Related Error:\n')
                        print(e)
                        print('\nAttempting to email without TLS/SSL\n')

                        if server:
                                server.quit()

                        server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)
                        server.login(cfg.account, cfg.password)

                message = 'Subject: {}\n\n{}'.format(cfg.subject, 'Notification test from RTORRENT-IMDB-DISK-CHECKER. All good!')
                server.sendmail(cfg.account, cfg.receiver, message)
                server.quit()
                print('Succeeded')
        except Exception as e:
                print('Failed\n\nNon TLS/SSL Related Error:\n')
                print(e)

def send_slack():
        slack_data = {
                'text': 'Notification test from RTORRENT-IMDB-DISK-CHECKER. All good!',
                'username': cfg.slack_name,
                'icon_emoji': ':white_check_mark:'
        }
        req = Request(cfg.slack_webhook_url)
        response = urlopen(req, json.dumps(slack_data).encode('utf8')).read()
        if response.decode('utf8') != 'ok':
                print('Failed to send slack notification, check slack_webhook_url.')

try:
        if sys.argv[1] == 'email':
                send_email()
                sys.exit()

        if sys.argv[1] == 'slack':
                send_slack()
                sys.exit()
        
        torrent_size = float(sys.argv[1])
        script_path = os.path.dirname(sys.argv[0])
        queue = script_path + '/queue.txt'
        remover = script_path + '/remover.py'
        remover_queue = script_path + '/' + 'hash'
        emailer = script_path + '/emailer.py'
        last_torrent = script_path + '/hash.txt'
        downloading = xmlrpc('d.multicall2', ('', 'leeching', 'd.left_bytes='))
        downloading = 0
        all_path = [path for path in cfg.maximum_space_quota]
        mp_space, quota_mp, min_sp = {}, {}, {}
        for mp in mount_points:
                if mount_points[mp] not in all_path:
                        all_path.append(mount_points[mp])
                        disk = os.statvfs(mount_points[mp])
                        mp_space[mount_points[mp]] = disk.f_bsize * disk.f_bavail
                        for quota_path in all_path:
                                if quota_path.find(mount_points[mp]) == 0:
                                        quota_mp[quota_path]=mount_points[mp]
        completed_copy = completed[:]
        for tested_path in all_path:
                if not os.path.exists(tested_path):
                        print('Incorrect path %s in maximum_space_quota in config.py' % (tested_path))
                        continue
                elif tested_path in cfg.maximum_space_quota:
                        quota_free = cfg.maximum_space_quota[tested_path] * 1073741824 - disk_usage(tested_path)
                        disk_free = mp_space[quota_mp[tested_path]]
                        if disk_free < quota_free:
                                continue
                else:
                        disk_free = quota_free = mp_space[tested_path]
                available_space = (min(disk_free, quota_free) - downloading) / 1073741824.0
                if tested_path in cfg.minimum_space_mp:
                        minimum_space = cfg.minimum_space_mp[tested_path]
                elif tested_path in quota_mp and quota_mp[tested_path] in cfg.minimum_space_mp:
                        minimum_space = cfg.minimum_space_mp[quota_mp[tested_path]]
                else:
                        minimum_space = cfg.minimum_space
                min_sp[tested_path] = minimum_space
                required_space = torrent_size - (available_space - minimum_space)
                requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.minimum_seeders, cfg.fallback_age, cfg.fallback_ratio
                current_date = datetime.now()
                include = override = True
                exclude = no = False
                freed_space = count = 0
                fallback_torrents, deleted = [], []

                while freed_space < required_space:

                        if not completed and not fallback_torrents:
                                break

                        if completed:
                                t_age, t_label, t_tracker, t_ratio, t_size_b, t_name, t_hash, t_path, parent_directory = completed[0]

                                if override:
                                        override = False
                                        min_size, min_age, min_ratio, min_seed, fb_age, fb_ratio = requirements

                                if cfg.exclude_unlabelled and not t_label:
                                        del completed[0]
                                        continue

                                if cfg.labels:

                                        if t_label in cfg.labels:
                                                label_rule = cfg.labels[t_label]
                                                rule = label_rule[0]

                                                if rule is exclude:
                                                        del completed[0]
                                                        continue

                                                if rule is not include:
                                                        override = True
                                                        min_size, min_age, min_ratio, fb_age, fb_ratio = label_rule

                                        elif cfg.labels_only:
                                                del completed[0]
                                                continue

                                if cfg.trackers and not override:
                                        tracker_rule = [tracker for tracker in cfg.trackers for url in t_tracker if tracker in url[0]]

                                        if tracker_rule:
                                                tracker_rule = cfg.trackers[tracker_rule[0]]
                                                rule = tracker_rule[0]

                                                if rule is exclude:
                                                        del completed[0]
                                                        continue

                                                if rule is not include:
                                                        override = True
                                                        min_size, min_age, min_ratio, min_seed, fb_age, fb_ratio = tracker_rule

                                        elif cfg.trackers_only:
                                                del completed[0]
                                                continue

                                t_age = (current_date - datetime.utcfromtimestamp(t_age)).days
                                t_ratio /= 1000.0
                                t_size_g = t_size_b / 1073741824.0
                                t_seed = max([tracker[1] for tracker in t_tracker])

                                if t_seed < min_seed:
                                        del completed[0]
                                        continue

                                if t_age < min_age or t_ratio < min_ratio or t_size_g < min_size:

                                        if fb_age is not no and t_age >= fb_age and t_size_g >= min_size:
                                                fallback_torrents.append([parent_directory, t_age, t_label, t_tracker, t_size_g, t_name])

                                        elif fb_ratio is not no and t_ratio >= fb_ratio and t_size_g >= min_size:
                                                fallback_torrents.append([parent_directory, t_age, t_label, t_tracker, t_size_g, t_name])

                                        del completed[0]
                                        continue

                                del completed[0]
                        else:
                                parent_directory, t_age, t_label, t_tracker, t_size_g, t_name = fallback_torrents[0]
                                del fallback_torrents[0]

                        if (tested_path not in quota_mp and mount_points[parent_directory] != mount_points[tested_path]) or (tested_path in quota_mp and (mount_points[parent_directory] != quota_mp[tested_path] or tested_path not in parent_directory)):
                                continue
                        
                        count += 1
                        freed_space += t_size_g
                        deleted.append('%s. Age    : %s Days Old\n   Name   : %s\n   Size   : %s GB\n   Label  : %s\n   Tracker: %s\n' % (count, t_age, t_name, t_size_g, t_label, t_tracker[0][0]))


                time = datetime.now() - start
                start = datetime.now()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                calc = available_space + freed_space - torrent_size

                with open('testresult.txt', 'a+') as textfile:
                        textfile.write('\n===== Test for Torrent Download in %s =====\n\n%s' % (tested_path, now))
                        textfile.write('\nExecuted in %s seconds\n%s Torrent(s) Deleted Totaling %.2f GB\n' % (time, count, freed_space))
                        textfile.write('%.2f GB Free Space Before Torrent Download (minimum space %.2f GB)\n%.2f GB Free Space After %.2f GB Torrent Download\n\n' % (available_space, min_sp[tested_path], calc, torrent_size))

                        for result in deleted:

                                if sys.version_info[0] == 3:
                                        textfile.write(result + '\n')
                                else:
                                        textfile.write(result.encode('utf-8') + '\n')

                print('\n===== Test for Torrent Download in %s =====\n\n%s' % (tested_path, now))
                print('Executed in %s seconds\n%s Torrent(s) Deleted Totaling %.2f GB' % (time, count, freed_space))
                print('%.2f GB Free Space Before Torrent Download (minimum space %.2f GB)\n%.2f GB Free Space After %.2f GB Torrent Download\n' % (available_space, min_sp[tested_path], calc, torrent_size))
                for result in deleted:
                        print(result)
                completed = completed_copy[:]


except Exception as e:
        print(e)

try:
        xmlrpc('d.multicall2', ('', 'leeching', 'd.down.total='))
except:
        print('SCGI address not configured properly. Please adjust it in your config.py file before continuing.')
        sys.exit()