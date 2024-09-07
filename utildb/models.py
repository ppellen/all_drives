#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        models.py
# Purpose:
#
# Author:      pp
#
# Created:     27/08/2024
# Copyright:   (c) pp 2024
# Licence:
# -------------------------------------------------------------------------------
from oauthlib.uri_validate import query
from peewee import *

from utildb.definedbs import database_disks
# from playhouse.shortcuts import model_to_dict

db = SqliteDatabase( database_disks, pragmas={'foreign_keys': 1})  # **{})

class BaseModel(Model):
    class Meta:
        database = db


class Disk(BaseModel):
    id = IntegerField(primary_key=True)
    external_disk_name = TextField()  #  'mypassport'
    mountpoint         = TextField()  #  '/media/pp/mypassport'
    # class Meta:
    #     table_name = 'costs_definitions'

    def get_disk_info(disk_id):
        try:
            query = (Disk.select().where(Disk.id==disk_id))
            this_disk = query[0]
        except ValueError as e:
            raise(e)

        # return model_to_dict(this_disk)
        return this_disk


class Folder(BaseModel):
    id = IntegerField(primary_key=True)
    # disk_id = ForeignKeyField(Disk, backref='folders')   # -> Premier caractère de mat_path.
    parent_id = IntegerField(null=False)  # root folder has id 0.
    # parent_folder = ForeignKeyField(Folders, backref='folders') ça, ça ne fonctionne pas. (Pas "Foreign")
    # Voir "Self-referential foreign keys" dans http://docs.peewee-orm.com/en/latest/peewee/models.html#self-referential-foreign-keys
    parent_folder = ForeignKeyField('self', null=True, backref='children')  # the foreign key points upward to the
    # parent object and the back-reference is named children.
    mat_path = TextField(null=True)  # materialized path
    folder_name= TextField(null=True)
    folder_last_access = DateField(null=True)  # stat.st_atime
    folder_last_modif  = DateField(null=True)  # stat.st_mtime
    folder_meta_change = DateField(null=True)  # stat.st_ctime
    # class Meta:
    #     table_name = 'folders'
    def initialize(self):
        pass
        return True

    def get_folder_info(folder_id):
        try:
            query = (Folder.select().where(Folder.id==folder_id))
            this_folder = query[0]
        except ValueError as e:
            raise(e)
        return this_folder

class Extension(BaseModel):
    id = IntegerField(primary_key=True)
    extension = TextField(null=True)
    size = IntegerField(null=True)
    count = IntegerField(null=True)


class File(BaseModel):
    id = IntegerField(primary_key=True)
    folder_id = ForeignKeyField(Folder, backref='files')
    extension = ForeignKeyField(Extension, backref='files')
    file_name = TextField(null=True)
    file_size = IntegerField(null=False)
    file_last_access = DateField(null=True)  # stat.st_atime
    file_last_modif  = DateField(null=True)  # stat.st_mtime
    file_meta_change = DateField(null=True)  # stat.st_ctime
    hexdigest = TextField(null=True)
    file_mat_path = TextField(null=True)  # materialized path to this file
    # class Meta:
    #     table_name = 'files'

    def get_full_path(self):
        try:
            query = (Folder.select().where(Folder.id==self.folder_id))
            my_folder_inst = query[0]
            my_folder_mat_path = my_folder_inst.mat_path + '.' + str(my_folder_inst.id)
        except ValueError as e:
            raise(e)

        return my_folder_mat_path

    def __init__(self, **kwargs):
        # BaseModel.__init__(self, **kwargs)    # TODO : vraiment OK ?
        super().__init__(**kwargs)
        self.file_mat_path = self.get_full_path()


# Reliquat d'une utilisation de pwiz en 2018 ? La classe UnknownField.
# class UnknownField(object):
#     def __init__(self, *_, **__): pass
# https://github.com/coleifer/peewee/issues/1916
# peewee update thrown exception 'UnknownField' object has no attribute 'get_sort_key' #1916

# class SqliteSequence(BaseModel):
#     name = UnknownField(null=True)  #
#     seq = UnknownField(null=True)  #
#
#     class Meta:
#         table_name = 'sqlite_sequence'
#         primary_key = False


if __name__ == "__main__":
    if True:
        db.connect(reuse_if_open=True)

        #  tables = db.get_tables()
        # db.drop_tables(db.get_tables())  #  NOK  trouvé sur stackoverflow, ne fonctionne pas car db.get_tables()
        # retourne les noms des tables (des str) alors que drop_tables demande des Models.
        # Concernant drop_all() : pas trouvé.
        try:
            #  db.drop_tables(db.get_tables())  # NOK ("'str' object has no attribute '_meta'",)
            db.drop_tables([Disk, Folder, File, Extension])
            db.create_tables([Disk, Folder, File, Extension])
        except Exception as error:
            print(error.args)   # ("'str' object has no attribute '_meta'",)
            # raise(error)
        finally:
            db.close()
