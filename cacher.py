# -*- coding: utf-8 -*-

import sys, os, time, shutil, pprint
from datetime import datetime, timedelta
from remotecaller import xmlrpc

script_path = os.path.dirname(sys.argv[0])
lock = script_path + '/cachelock.txt'
torrent_cache = script_path + '/torrents.py'
cache_copy = script_path + '/torrentscopy.py'
mp_cache = script_path + '/mountpoints.py'

def enter(identity):
        if os.path.isfile(lock):
                with open(lock, 'r') as txt:
                        running_id, running_start = txt.read().strip().splitlines()[0].split()
                if (running_id == 'schedule' and int(time.time()) - running_start < timedelta(seconds=30)) or (identity == 'schedule' and running_id == 'checker'):
                        sys.exit()
        with open(lock, 'w') as txt:
                txt.write(identity + '\n')

def leave(identity):
        os.remove(lock)

def folder_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def build_cache(identity):
        enter(identity)
        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=,t.scrape_complete=', 'd.ratio=', 'd.size_bytes=', 'd.name=', 'd.hash=', 'd.directory='))
        completed.sort()
        [list.append(list[7].rsplit('/', 1)[0]) if list[5] in list[7] else list.append(list[7]) for list in completed]
        leeching = xmlrpc('d.multicall2', ('', 'leeching', 'd.left_bytes=', 'd.custom1=', 't.multicall=,t.url=,t.scrape_complete=', 'd.ratio=','d.size_bytes=', 'd.name=', 'd.hash=', 'd.directory='))
        [list.append(list[7].rsplit('/', 1)[0]) if list[5] in list[7] else list.append(list[7]) for list in leeching]
        if xmlrpc('system.file.allocate',('',)):
                for list in leeching:
                        if list[5] in list[7]:
                                list[0]=list[4]-folder_size(list[7])
                        else:
                                list[0]=list[4]-os.stat(list[7]+list[5]).st_size
        cache = open(cache_copy, mode='w+')
        cache.write('completed = ' + pprint.pformat(completed))
        cache.write('\n\nleeching = ' + pprint.pformat(leeching))
        shutil.move(cache_copy, torrent_cache)
        leave(identity)

        if not os.path.isfile(mp_cache):
                mount_points = {}
        else:
                from mountpoints import mount_points
                mp_updated = False
        for list in completed + leeching:
                parent_directory = list[8]
                if parent_directory not in mount_points:
                        mp_updated = True
                        mount_point = [path for path in [parent_directory.rsplit('/', num)[0] for num in range(parent_directory.count('/'))] if os.path.ismount(path)]
                        mount_point = mount_point[0] if mount_point else '/'
                        mount_points[parent_directory] = mount_point
        if mp_updated:
                open(mp_cache, mode='w+').write('mount_points = ' + pprint.pformat(mount_points))

if __name__ == "__main__":
        build_cache('schedule ' + str(int(time.time())))
