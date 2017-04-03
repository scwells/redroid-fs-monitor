import sys
import time
import logging
import shutil
import os
import time
import datetime
import ntpath
from threading import Thread
import subprocess
import re

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

log_file_path = '/home/redroid/video_saves/redroid-fs-monitor/fs_monitor.log'
video_save_path = '/home/redroid/video_saves/'
index_flv_script_path = '/home/redroid/video_saves/redroid-fs-monitor/flvlib-0.1.7/scripts/index-flv'
username = 'redroid'
flv_regex = re.compile('\A.*(.flv)\Z')
# public_webportal_path = '/home/redroid/webportal/public/videos/'

def stream_incomplete(filepath):
    # print filepath
    temp_grep_file = filepath + '_grep.temp'
    grep_process = subprocess.call('sudo lsof | grep nginx >' + temp_grep_file, shell=True)
    with open(temp_grep_file, 'r') as grep_file:
        for line in grep_file.readlines():
            if line.split()[-1] == filepath:
                return True
    os.remove(temp_grep_file)
    return False

def get_filename(video_save_path):
    head, tail = ntpath.split(video_save_path)
    return tail or ntpath.basename(head)

def append_to_log(log):
    with open(log_file_path, 'ab') as f:
        f.write('{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()) +' [' + log + ']\n')

def flv_thread_function(event):
    if not event.is_directory:
        try:
            if '_' not in get_filename(event.src_path):
                raise
            directory_path = get_filename(event.src_path).split('_')[0] # split filename on underscore'
        except Exception as e:
            append_to_log('Error: Invalid File Name ' + event.src_path)
            return
        # create the folder here (do nothing if exists already)
        try:
            os.makedirs(video_save_path + directory_path)
            os.chmod(video_save_path + directory_path, 0o777 )
            append_to_log('Created Directory: ' + video_save_path + directory_path)
            #os.makedirs(public_webportal_path + directory_path)
            #append_to_log('Created Directory: ' + public_webportal_path + directory_path)
        except OSError as e:
            append_to_log('Error : ' + str(e))
            pass

        try:
            while stream_incomplete(event.src_path):
                time.sleep(5)


            os.chmod(event.src_path, 0o666 )
            index_process = subprocess.Popen([index_flv_script_path, '-U', event.src_path])
            index_process.wait()
            # print 'after script'

            append_to_log('FLV Indexed: ' + event.src_path)
            # move file into correct directory
            shutil.move(event.src_path, video_save_path + directory_path)
            filename = get_filename(event.src_path)
            append_to_log('File Moved: ' + filename)
            os.symlink(video_save_path + directory_path + '/' + filename, video_save_path  + '/vod_links/' + filename)
            append_to_log('Symlink Created: ' + filename)
            
            # change file permissions (running this script as root.. I have no choice :( )
            os.chmod(video_save_path  + '/vod_links/' + filename, 0o666 )

        except Exception as e:
            append_to_log('Error : ' + str(e))
            return


class FileCreatedHandler(FileSystemEventHandler):
    def on_created(self, event):
        if(flv_regex.match(event.src_path)):
            Thread(target=flv_thread_function, args=(event,)).start()


if __name__ == "__main__":
    event_handler = FileCreatedHandler()
    observer = Observer()
    observer.schedule(event_handler, video_save_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
