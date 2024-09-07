import os
from datetime import datetime, timezone

dirs_size = 0
files_size = 0

root = '/home/pp/dev/sw/PycharmProjects/'  #  '/media/pp/mypassport/'

for root, dirs, files in os.walk(root, followlinks=False ):
    for dd in dirs:
        this_stat = os.stat(os.path.join(root,dd), follow_symlinks=False)
        print(os.path.join(root,dd),
              this_stat.st_size,'\n',
              'last access: ', datetime.fromtimestamp(this_stat.st_atime, tz=timezone.utc).strftime('%Y-%m-%d %H:%M'),'\n',
              'last modif:  ', datetime.fromtimestamp(this_stat.st_mtime, tz=timezone.utc).strftime('%Y-%m-%d %H:%M'),'\n',
              'meta change: ', datetime.fromtimestamp(this_stat.st_ctime, tz=timezone.utc).strftime('%Y-%m-%d %H:%M'),'\n')
        pass

    dirs_size += len(dirs)
    files_size += len(files)

print(f'dirs: {dirs_size}. files: {files_size}')