import sys
import time
import logging
import shutil
import os
import datetime
import ntpath

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

log_file_path = './fs_monitor.log'
video_save_path = '/home/redroid/video_saves/'
# public_webportal_path = '/home/redroid/webportal/public/videos/'

def get_filename(video_save_path):
    head, tail = ntpath.split(video_save_path)
    return tail or ntpath.basename(head)

def append_to_log(log):
    with open(log_file_path, 'ab') as f:
        f.write('{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()) +' [' + log + ']\n')

class FileCreatedHandler(FileSystemEventHandler):
    def on_created(self, event):
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
                append_to_log('Created Directory: ' + video_save_path + directory_path)
                #os.makedirs(public_webportal_path + directory_path)
                #append_to_log('Created Directory: ' + public_webportal_path + directory_path)
            except OSError:
                pass

            try:
                shutil.move(event.src_path, video_save_path + directory_path)
                filename = get_filename(event.src_path)
                append_to_log('File Moved: ' + filename)
                #os.symlink(video_save_path + directory_path + '/' + filename, public_webportal_path + directory_path + '/' + filename)
                #append_to_log('Symlink Created: ' + filename)
            except Exception as e:
                append_to_log('Error : ' + e)
                pass


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
