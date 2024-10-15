# traverse_folders
# -- differently --
# New version with chdir(down), process, chdir(up)

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from os import chdir, walk, sep, stat, getcwd, listdir
from os.path import islink, isfile, isdir, splitext
from shutil import disk_usage

from discover_disk import discover_disk
from test1_chdir import root_folder

from datetime import datetime, timezone
import pytz

import hashlib

from utildb.models_new import db, Disk, Folder, File, Extension

from peewee import fn

tz_paris = pytz.timezone('Europe/Paris')

def datetime_fromtimestamp(this_time):
    return datetime.fromtimestamp(this_time, tz=tz_paris).strftime("%Y-%m-%d  %H:%M")  # timezone.utc NOK  :%S

def db_get_max_ids():
    max_disk_id = Disk.select(fn.Max(Disk.id)).scalar()
    max_folder_id = Folder.select(fn.Max(Folder.id)).scalar()
    max_file_id = File.select(fn.Max(File.id)).scalar()
    max_extension_id = Extension.select(fn.Max(Extension.id)).scalar()

    if max_disk_id is None: max_disk_id = 0
    if max_folder_id is None: max_folder_id = 0
    if max_file_id is None: max_file_id = 0
    if max_extension_id is None: max_extension_id = 0
    return     max_disk_id ,    max_folder_id ,     max_file_id ,     max_extension_id

class data_file(object):

    def __init__(self, root, name):
        self.root = root
        self.name = name
        self.fullname = root+sep+name
        self.statinfo = stat(self.fullname, follow_symlinks=False)
        with open(self.fullname, "rb") as this_opened_file:
            buf = this_opened_file.read()
            self.digest = hashlib.md5(buf)


def process_file( current_folder, this_file, current_folder_inst ):

    must_create_extension = False
    this_extension_inst = None  # inst : instance

    filename_wo_extension, extension_txt = splitext(this_file)
    if len(extension_txt) != 0:
        if extension_txt[0] == '.':
            extension_txt = extension_txt[1:]

    try:
        this_extension_inst = Extension.get(Extension.extension==extension_txt)
    except Exception as e:
        # print(repr(e))
        this_extension_inst = Extension.create(extension=extension_txt, count=0, size=0)
        this_extension_inst.save()
        # raise(e)

    # extension = ForeignKeyField(Extension, backref='files')
    file_data = data_file(current_folder,this_file)

    # See https://docs.peewee-orm.com/en/latest/peewee/api.html#DateTimeField
    if True:  # this_file == 'file0.1-test.txt':
        # Compute mat_path
        my_folder_mat_path = current_folder_inst.mat_path + '.' + str(current_folder_inst.id)
        file_inst = File.create(folder_id= current_folder_inst.id,
                              extension=this_extension_inst.id,
                              file_name=this_file,
                              file_mat_path= my_folder_mat_path,
                              file_size=file_data.statinfo.st_size,
                              # file_last_access =  datetime_fromtimestamp(file_data.statinfo.st_atime),
                              file_last_modif =   datetime_fromtimestamp(file_data.statinfo.st_mtime),
                              # file_meta_change =  datetime_fromtimestamp(file_data.statinfo.st_ctime),
                              hexdigest = file_data.digest.hexdigest()
        )
        file_inst.save()

    this_extension_inst.size += file_data.statinfo.st_size
    this_extension_inst.count += 1
    this_extension_inst.save()


def process_folder(parent_folder_inst, this_folder_name ):

    # -2 Avoid appimage folder !
    if this_folder_name == 'appimage':
        return


    # -1 - Are we allowed ? stat.st_uid == stat.st_gid == 0 => owner is root.
    target_folder = '.'+sep+this_folder_name

    # pb 'dbus-1.0'
    try:
        stat_info =  stat(target_folder, follow_symlinks=False)
    except:
        print('current folder: ', getcwd())
        print('impossible stat de ',target_folder )
        print('returning')
        return

    if stat_info.st_uid == 0 or stat_info.st_gid == 0:
        print('current folder: ', getcwd())
        print('!!! stat_info.st_uid == 0 or stat_info.st_gid == 0 for folder:',target_folder )
        print('returning')
        return

    # 0 - where are we
    chdir(target_folder)
    current_folder = getcwd()

    # 1 - create this folder in db
    mat_path = parent_folder_inst.mat_path + '.' + str(parent_folder_inst.id)


    test = True  # TODO
    stat_info = stat(current_folder, follow_symlinks=False)
    current_folder_inst = Folder.create(
        parent_folder = parent_folder_inst.id,
        mat_path = mat_path,
        folder_name= this_folder_name,
        # folder_last_access = datetime_fromtimestamp(stat_info.st_atime),
        folder_last_modif  = datetime_fromtimestamp(stat_info.st_mtime),
        # folder_meta_change = datetime_fromtimestamp(stat_info.st_ctime),
    )
    current_folder_inst.save()

    # 2 - process files in this folder
    if True:
        list_of_files = [name_ for name_ in listdir(current_folder) if isfile(current_folder + sep+ name_) ]
        for _file in list_of_files:
            process_file( current_folder, _file, current_folder_inst)

    # 3 - process folders below.
    list_of_folders = [ name_ for name_  in listdir(current_folder) if
                        ( isdir(current_folder + sep + name_) and not islink(current_folder + sep + name_))]
    if len(list_of_folders) > 0:
        # TODO
        if 'share' in  list_of_folders:
            print("'share' in  list_of_folders !!!")
            pass
        for folder_below in list_of_folders:
            process_folder(current_folder_inst, folder_below)

    # 4 - back upwards.
    chdir('..')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    db.connect(reuse_if_open=True)
    try:
        db.create_tables([Disk, Folder, File, Extension])
    except Exception as error:
        print(error.args)  # ("'str' object has no attribute '_meta'",)
        # raise(error)
    finally:
        pass
    max_ids_at_start_disk = db_get_max_ids()
    current_dir = getcwd()

    test = True  # TODO
    if not test:
        external_disk_name, this_mountpoint = discover_disk()
        if external_disk_name is None or this_mountpoint is None:
            print("No external disk found - Not under test.")
            exit()
    else:
        this_mountpoint =  "/home/pp/dev/sw/PycharmProjects/all_drives/test"  #  "/media/pp/intenso/rsync_02.06.23/appimage/FreeCAD/usr/lib"  #
        external_disk_name = "test"  # Le dernier folder de this_mountpoint doit être = external_disk_name    "lib"  #

    disk_inst = Disk.create( external_disk_name = external_disk_name,
                             mountpoint         = this_mountpoint)
    disk_inst.save()

    stat_info_root = stat(this_mountpoint, follow_symlinks=False)

    pseudo_parent_name = sep.join(this_mountpoint.split(sep)[:-1])  #  [:-1]  means [0..-2] included

    root_folder_inst = Folder.create(
        parent_folder = None, #
        mat_path = str(disk_inst.id),  # materialized path - starts with disk id.
        folder_name= pseudo_parent_name,
        # folder_last_access = datetime_fromtimestamp(stat_info_root.st_atime),
        folder_last_modif  = datetime_fromtimestamp(stat_info_root.st_mtime),
        # folder_meta_change = datetime_fromtimestamp(stat_info_root.st_ctime),
    )
    root_folder_inst.save()
    chdir(pseudo_parent_name)
    process_folder(root_folder_inst , external_disk_name)

    try:
        query = Folder.select(Folder.id).where(Folder.parent_folder==root_folder_inst.id)
        disk_inst.id_disk_root_folder=query.scalar()
        disk_inst.save()
        pass
    except:
        pass

    chdir(current_dir)
    db.close()
    exit()
