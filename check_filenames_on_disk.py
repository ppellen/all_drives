import os
from datetime import datetime, timezone

dirs_size = 0
files_size = 0

root = '/home/pp/tmp/'  # '/media/pp/mypassport/'  #  '/home/pp/dev/sw/PycharmProjects/' 

# https://gist.github.com/doctaphred/d01d05291546186941e1b7ddc02034d3
# (github) doctaphred/ntfs-filenames.txt
# https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file

# handy list : <>:"/\|?*

forbidden_chars = "<>:/\\|?*"

# print(forbidden_chars)
# for c in forbidden_chars:
#     print(c in forbidden_chars)
# exit()


for root, dirs, files in os.walk(root, followlinks=False ):
    for dd in dirs:
        for c in dd:
            if c in forbidden_chars :
                print('(dir) ', os.path.join(root,dd))

    for ff in files:
        for c in ff:
            if c in forbidden_chars :
                print('(file) ', os.path.join(root,ff))
