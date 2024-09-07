from utildb.models import db, Disk, Folder, File, Extension


def print_all_mat_paths():
    for this_file_inst in File.select():
        this_path = File.get_full_path(this_file_inst)
        print(this_path)
        pass

def print_all_file_names_disks_paths():
    for this_file_inst in File.select():
        this_path = File.get_full_path(this_file_inst)
        path_splitted= this_path.split('.')
        my_disk = Disk.get_disk_info(int(path_splitted[0]))

        path_str = ''
        for folder_id in path_splitted[1:]:
            folder_info= Folder.get_folder_info(int(folder_id))
            path_str += folder_info.folder_name
            path_str += '/'

        print (my_disk.external_disk_name, path_str, this_file_inst.file_name)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db.connect(reuse_if_open=True)

    for this_file_inst in File.select():
        pass



