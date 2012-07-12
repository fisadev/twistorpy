Twistorpy
=========

Twitter history backup tool

Simple command-line tool / python module that allows to make a backup of the tweets of a twitter user on a json file. Limited to the newest 3200 tweets (twitter api limitation), plus those tweets of wich you know the tweet id. The user must have his tweets public.

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

