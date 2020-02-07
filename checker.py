#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, time, pprint, config as cfg
from subprocess import Popen, check_output
from datetime import datetime, timedelta
from remotecaller import xmlrpc

torrent_name = sys.argv[1]
torrent_label = sys.argv[2]
torrent_hash = sys.argv[3]
torrent_path = sys.argv[4]
torrent_size = int(sys.argv[5]) / 1073741824.0
is_meta = True if sys.argv[5] == '1' else False

def disk_usage(path):
        try:
                used_k = int(check_output(['du','-ks', path]).split()[0])
        except:
                used_k = 0
        return 1024 * used_k

def imdb_search():

        try:
                from threading import Thread
                from guessit import guessit
                from imdbpie import Imdb

                def imdb_ratings():
                        ratings.update(imdb.get_title_ratings(movie_imdb))

                def movie_country():
                        country.extend(imdb.get_title_versions(movie_imdb)['origins'])

                imdb = Imdb()
                torrent_info = guessit(torrent_name)
                movie_title = torrent_info['title'] + ' ' + str(torrent_info['year'])
                movie_imdb = imdb.search_for_title(movie_title)[0]['imdb_id']

                ratings = {}
                country = []
                t1 = Thread(target=movie_country)
                t2 = Thread(target=imdb_ratings)
                t1.start()
                t2.start()
                t1.join()
                t2.join()
        except:
                return

        rating = ratings['rating']
        votes = ratings['ratingCount']

        if rating < minimum_rating or votes < minimum_votes:
                xmlrpc('d.erase', (torrent_hash,))
                sys.exit()

        if skip_foreign and 'US' not in country:
                xmlrpc('d.erase', (torrent_hash,))
                sys.exit()

if torrent_label in cfg.imdb:
        minimum_rating, minimum_votes, skip_foreign = cfg.imdb[torrent_label]
        imdb_search()

if cfg.enable_disk_check and not is_meta and torrent_label != 'bypass':
        script_path = os.path.dirname(sys.argv[0])
        queue = script_path + '/queue.txt'

        with open(queue, 'a+') as txt:
                txt.write(torrent_hash + '\n')

        time.sleep(0.001)

        while True:

                try:
                        with open(queue, 'r') as txt:
                                queued = txt.read().strip().splitlines()
                except:
                        with open(queue, 'a+') as txt:
                                txt.write(torrent_hash + '\n')

                try:
                        if queued[0] == torrent_hash:
                                break

                        if torrent_hash not in queued:

                                with open(queue, 'a') as txt:
                                        txt.write(torrent_hash + '\n')
                except:
                        pass

                time.sleep(0.01)

        import cacher
        cacher.build_cache('checker ' + str(int(time.time())))
        from torrents import completed, leeching
        from mountpoints import mount_points

        current_time = datetime.now()
        remover = script_path + '/remover.py'
        remover_queue = script_path + '/' + torrent_hash + '.txt'
        subtractions = script_path + '/' + torrent_hash + 'sub.txt'
        notifier = script_path + '/notifier.py'
        mount_point = [path for path in [torrent_path.rsplit('/', num)[0] for num in range(torrent_path.count('/'))] if os.path.ismount(path)]
        mount_point = mount_point[0] if mount_point else '/'
        quota_path = [path for path in [torrent_path.rsplit('/', num)[0] for num in range(torrent_path.count('/'))] if path in cfg.maximum_size_quota]
        quota_path = quota_path[0] if quota_path else False
        
        disk = os.statvfs(mount_point)
        disk_free = disk.f_bsize * disk.f_bavail
        quota_free = 10**15
        if quota_path:
                quota_free = cfg.maximum_size_quota[quota_path] * 1073741824 - disk_usage(quota_path)
        try:
                from torrent import downloads
                mp_additions = []
                quota_additions = []
                downloads = [list for list in downloads if current_time - list[1] < timedelta(minutes=3)]
                mp_history = [(t_hash, mp_additions.append(add)) for p_dir, d_time, t_hash, add, q_add in downloads if mount_points[p_dir] == mount_point]
                quota_history = [(t_hash, quota_additions.append(q_add)) for p_dir, d_time, t_hash, add, q_add  in downloads if quota_path and quota_path in p_dir]
                mp_history = [list[0] for list in mp_history]
                quota_history = [list[0] for list in quota_history]
                try:
                        mp_unaccounted = sum(mp_additions) - sum(int(open(script_path + '/' + list + 'sub.txt').read()) for list in mp_history)
                except:
                        mp_unaccounted = 0
                try:
                        quota_unaccounted = sum(quota_additions) - sum(int(open(script_path + '/' + list + 'sub.txt').read()) for list in quota_history)
                except:
                        quota_unaccounted = 0
        except:
                downloads = []
                mp_downloading = quota_downloading = 0
                mp_unaccounted = quota_unaccounted = 0
        mp_downloading = sum(list[0] for list in leeching if mount_points[list[8]] == mount_point and list[6] != torrent_hash)
        quota_downloading = sum(list[0] for list in leeching if quota_path and quota_path in list[8] and list[6] != torrent_hash)
        mp_avail_space = (disk_free + mp_unaccounted - mp_downloading) / 1073741824.0
        quota_avail_space = (quota_free + quota_unaccounted - quota_downloading) / 1073741824.0
        minimum_space = cfg.minimum_space_mp[mount_point] if mount_point in cfg.minimum_space_mp else cfg.minimum_space
        mp_required_space = torrent_size - (mp_avail_space - minimum_space)
        quota_required_space = torrent_size - (quota_avail_space - minimum_space)
        requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.minimum_seeders, cfg.fallback_age, cfg.fallback_ratio
        include = override = True
        exclude = no = False
        mp_freed_space = quota_freed_space = deleted = quota_deleted = 0
        fallback_torrents, removable, removed = [], [], []

        while mp_freed_space < mp_required_space or quota_freed_space < quota_required_space:

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
                                                min_size, min_age, min_ratio, min_seed, fb_age, fb_ratio = label_rule

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

                        t_age = (current_time - datetime.utcfromtimestamp(t_age)).days
                        t_ratio /= 1000.0
                        t_size_g = t_size_b / 1073741824.0
                        t_seed = max([tracker[1] for tracker in t_tracker])

                        if t_age < min_age or t_ratio < min_ratio or t_size_g < min_size or t_seed < min_seed:

                                if fb_age is not no and t_age >= fb_age and t_size_g >= min_size:
                                        fallback_torrents.append((parent_directory, t_hash, t_path, t_size_b, t_size_g))

                                elif fb_ratio is not no and t_ratio >= fb_ratio and t_size_g >= min_size:
                                        fallback_torrents.append((parent_directory, t_hash, t_path, t_size_b, t_size_g))

                                del completed[0]
                                continue

                        del completed[0]
                else:
                        parent_directory, t_hash, t_path, t_size_b, t_size_g = fallback_torrents.pop(0)

                if mount_points[parent_directory] != mount_point:
                        continue
                elif quota_path and quota_path not in parent_directory and mp_freed_space >= mp_required_space:
                        continue
                elif quota_path and quota_path in parent_directory and quota_freed_space >= quota_required_space:
                        continue

                try:
                        xmlrpc('d.open', (t_hash,))
                except:
                        continue

                if not deleted:
                        open(subtractions, mode='w+').write('0')

                removable.append((t_size_g, t_hash, t_path))
                deleted += t_size_b
                mp_freed_space += t_size_g
                if quota_path and quota_path in parent_directory:
                        quota_freed_space += t_size_g
                        quota_deleted += t_size_b

        if mp_freed_space >= mp_required_space and (not quota_path or quota_freed_space >= quota_required_space):
                #if last removed torrent is large, maybe some smaller removed torrents can stay
                removable.sort()
                mp_extra_space = mp_freed_space - mp_required_space
                quota_extra_space = quota_freed_space - quota_required_space
                while removable:
                        t_size_g, t_hash, t_path = removable.pop()
                        if t_size_g < mp_extra_space and t_size_g < quota_extra_space:
                                mp_extra_space -= t_size_g
                                quota_extra_space -= t_size_g
                                deleted -= t_size_g
                                quota_deleted -= t_size_g
                        else:
                                removed.append((t_size_g, t_hash, t_path))
                while removed:
                        t_size_g, t_hash, t_path = removed.pop()
                        Popen([sys.executable, remover, remover_queue, t_hash, t_path, subtractions])
                xmlrpc('d.start', (torrent_hash,))
        elif cfg.notification_email or cfg.notification_slack or cfg.notification_telegram:
                Popen([sys.executable, notifier])
        downloads.insert(0, (torrent_path, current_time, torrent_hash, deleted, quota_deleted))
        open(script_path + '/torrent.py', mode='w+').write('import datetime\ndownloads = ' + pprint.pformat(downloads))

        queue = open(queue, mode='r+')
        queued = queue.read().strip().splitlines()
        queue.seek(0)
        [queue.write(torrent + '\n') for torrent in queued if torrent != torrent_hash]
        queue.truncate()

        time.sleep(300)
        os.remove(subtractions)
else:
        xmlrpc('d.start', tuple([torrent_hash]))
