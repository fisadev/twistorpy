Twistorpy
=========

Twitter history backup tool

Simple command-line tool / python module that allows you to make a backup of the tweets of a twitter user on a json file. The user must have his tweets public.

Because of twitter api limits, each time you run the backup it will fetch tweets until the 3200th tweet is reached (from newer to older), and store them with the already backuped tweets. Plus you can fetch those tweets of which you know the tweet id.

Also, you can stop the running backup with ``Ctrl+c``, and the backup won't be corrupted. After that you could re-run the backup and it will add only the non-added tweets.

Basic usage
===========

``python twistorpy.py TWITTER_USER HISTORY_FILE_PATH [EXTRA_IDS_FILE_PATH]``

* **HISTORY_FILE_PATH**

Is the path for the json file. If the file doesn't exist, it will be created,
if it already exists, only new tweets will be added to the file.

* **EXTRA_IDS_FILE_PATH (optional)**

You can create a txt file with tweets ids, and those tweets will be downloaded
and added to the history if they don't exist.
(each line of the file must be a different tweet id)

