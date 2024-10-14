
from utildb.models_new import db, Disk, Folder, File, Extension


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
        db.connect(reuse_if_open=True)

        File.delete().execute()
        Extension.delete().execute()
        Folder.delete().execute()
        Disk.delete().execute()
        db.close()
        exit()

