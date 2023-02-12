## Fork notes

#### New features in this version, compared to JDRIVO version :

- python 2 and 3 compatible
- setting : maximum size quota for folders
- allow system.file.allocate = 1
- test is done on all mountpoints
- option to not remove hardlinked torrents
- lightweight: no python script running in background
- allow to bypass disk check with label 'bypass'
- if last removed torrent is large, some smaller removed torrents can stay (optimization)

## Script Explanation

#### This script is capable of the following functions when a torrent is added to rtorrent :

**1**. It can check your available disk space. If your free disk space is not large enough to accommodate a pending torrent, the script will delete torrents based on criteria defined in [config.py](https://github.com/twolaw/RTORRENT-IMDB-DISK-CHECKER/blob/master/config.py). The script will scan through your torrents from oldest to newest, ensuring the oldest torrent that meets your criteria is deleted first. If your disk space is still too low, the torrent will be sent to rtorrent in a stopped state.	

**2**. It can check the IMDB ratings/votes of a movie. The script will delete a movie torrent if its IMDB rating/votes don't meet your minimum requirements.

Requirements:
- rtorrent 0.9.7 or more recent
- python 2 or 3

## [Setup](https://github.com/twolaw/RTORRENT-IMDB-DISK-CHECKER/blob/master/setup.sh)

Run the setup script by entering the following command in your terminal (Refer to this script for manual setup instructions):

`bash setup.sh`

## [Test Script](https://github.com/twolaw/RTORRENT-IMDB-DISK-CHECKER/blob/master/test.py)

#### This script will show you what torrents the script will delete without actually deleting torrents.

Results will output to your terminal and a text file named **testresult.txt**

Enter the following command in your terminal to run it:

`python test.py 69`

**69** = torrent size in gigabytes

You can test notification:
`python test.py telegram` (or `email` or `slack`)
