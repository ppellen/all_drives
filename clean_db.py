
from utildb.models import Disk, Folder, File, Extension


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
        File.delete().execute()
        Extension.delete().execute()
        Folder.delete().execute()
        Disk.delete().execute()
        exit()

