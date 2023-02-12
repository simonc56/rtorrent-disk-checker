include = yes = True
exclude =  no = False

############ USER DEFINED VARIABLES START ############

# SCGI address or unix socket file path found in your rtorrent.rc file
scgi = '127.0.0.1:5000'

# Check disk space before downloading a torrent?
enable_disk_check = yes

# Receive an email when disk is full?
notification_email = no

# Receive slack or telegram notification when disk is full?
notification_slack = no
notification_telegram = no

###### EMAIL / SLACK SETTINGS - IGNORE IF DISABLED ######

# python test.py email | will send a test email
# python test.py slack | will send a test slack notification

# Amount of minutes to wait before sending a notification between torrent downloads
interval = 60
message = 'New torrent cannot start!\n\nSeedbox disk is full or quota has been reached.\nFree disk space ASAP and consider lowering minimum requirements rules.'

# Email
smtp_server = 'smtp.gmail.com'
port = 587
account = 'youremail@gmail.com'
password = 'yourpassword'
receiver = 'youremail@gmail.com'
subject = 'Warning: Seedbox Disk Full'

# Slack
slack_webhook_url = 'https://hooks.slack.com/services/************'
slack_icon = ':warning:'
slack_name = 'Seedbox'

# Telegram
telegram_token = '***:*****'
telegram_chat_id = '****'


###### DISK CHECK SECTION - IGNORE IF DISABLED ######

# This script will auto detect mount points and only delete torrents inside the moint point that the torrent will be downloaded to

# The minimum amount of free space (in Gigabytes) to maintain
minimum_space = 1

# Optional - Specify minimum space values for specific mount points
minimum_space_mp = {
#                          '/' : 5,
#                          '/torrents' : 100,
                   }

# Optional - Specify maximum size for specific directories (quota)
maximum_size_quota = {
#                          '/home/user001' : 50,
#                          '/torrents/music' : 300,
                      }
# GENERAL RULES START

# All minimum requirements must be met by a torrent to be deleted

# Torrent Size in Gigabytes / Age in Days

minimum_size = 5
minimum_age = 7
minimum_ratio = 1.2
minimum_seeders = 0

# Only the age of a torrent must be higher or equal to this number to be deleted (torrent size requirement remains) - no to disable
fallback_age = no

# Only the ratio of a torrent must be higher or equal to this number to be deleted (torrent size requirement remains) - no to disable
fallback_ratio = 1.1

# A torrent with a hardlink elsewhere in filesystem will not be removed - no to disable
exclude_hardlinked = yes

# GENERAL RULES END


# Tracker Rules will override general rules - Fill to enable

# include: use general rules | exclude: exclude tracker

# Value Order: 1. Minimum Torrent Size (GB) 2. Minimum Age 3. Minimum Ratio 4. Minimum seed 5. Fallback Age 6. Fallback Ratio

trackers = {
#                     'demonoid.pw' : [include],
#                     'hdme.eu' : [exclude],
#                     'redacted.ch' : [1, 7, 1.2, 10, no, no],
#                     'hd-torrents.org' : [3, 5, 1.3, 0, 9, 1.3],
#                     'privatehd.to' : [5, 6, 1.2, 2, 12, no],
#                     'apollo.rip' : [2, 5, 1.4, 0, no, 1.8],
           }

# Only delete torrents from trackers with a tracker rule (yes/no)
trackers_only = yes


# Label Rules will override general/tracker rules - Fill to enable

# include: use general/tracker rules | exclude: exclude label

# Value Order: 1. Minimum Torrent Size (GB) 2. Minimum Age 3. Minimum Ratio 4. Minimum seed 5. Fallback Age 6. Fallback Ratio

labels = {
#                     'Trash' : [include],
#                     'TV' : [exclude],
#                     'HD' : [1, 5, 1.2, 5, 15, 1.2],
         }

# Only delete torrents with labels that have a label rule (yes/no)
labels_only = no

# Exclude torrents without labels (yes/no)
exclude_unlabelled = no


###### IMDB SECTION - IGNORE IF UNWANTED ######

# The IMDB function will only execute if the torrent is attached to a label with an IMDB rule

# Value Order: 1. Minimum IMDB Rating 2. Minimum Votes 3. Skip Foreign Movies (yes/no)

imdb = {
#                     'Hollywood Blockbusters' : [7, 80000, yes],
#                     'Bollywood Classics' : [8, 60000, no],
       }

############ USER DEFINED VARIABLES END ############
