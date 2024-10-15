from time import strftime

from apt.auth import update

from utildb.models_new import Folder, File
from peewee import fn
#  About sqlite functions :
#  These functions only work for dates between 0000-01-01 00:00:00 and 9999-12-31 23:59:59
#  (julian day numbers 1721059.5 through 5373484.5). For dates outside that range, the results of these functions are undefined.

from datetime import datetime

MINDATE = datetime(1970,  1,  1,  0,  0,  0)
MAXDATE = datetime(9999, 12, 31, 23, 59, 59)

indent_level = 0

def indents():
    global indent_level
    return indent_level*"  "

def traverse( this_folder_id) :
    global indent_level
    #
    this_folder_inst = (Folder.select().where(Folder.id == this_folder_id)).execute()[0]
    print(indents(),"entering", repr(this_folder_inst))

    # query1 = Folder.select(fn.MIN(Folder.folder_last_modif),fn.MAX(Folder.folder_last_modif)).where(Folder.parent_folder == this_folder_id)  #
    query1 = Folder.select().where(Folder.parent_folder == this_folder_id)  #
    print(indents(), len(query1), ' folders')

    indent_level += 1
    for row_folder in query1:
        traverse(row_folder.id)

    query2 = File.select().where(File.folder_id == this_folder_id)  #
    print(indents(), len(query2), ' files')
    for row_file in query2:
        print(indents(), repr(row_file))

    indent_level -= 1

def traverse2( this_folder_id) :
    querymin = Folder.select(Folder.id, fn.MIN(Folder.folder_last_modif)).where(Folder.parent_folder == this_folder_id)
    querymax = Folder.select(Folder.id, fn.MAX(Folder.folder_last_modif)).where(Folder.parent_folder == this_folder_id)
    idmin , tmin = querymin.scalar(as_tuple=True)
    idmax , tmax = querymax.scalar(as_tuple=True)

    print(idmin, tmin)
    print(idmax, tmax)

    return     idmin , tmin, idmax , tmax

    print(len(query1), ' folders')
    for row_folder in query1:
        print(row_folder.id)
        traverse2(row_folder.id)

    query2 = File.select().where(File.folder_id == this_folder_id)  #
    print(len(query2), ' files')
    for row_file in query2:
        print(row_file.id)


def traverse3( this_folder_id) :

    print('Entering in folder/id :', this_folder_id)
    query1 = Folder.select(Folder.id, Folder.folder_last_modif).where(Folder.parent_folder == this_folder_id)
    same_parent = query1.tuples()
    if len(same_parent) > 0:
        result = [ s for  s in same_parent]
        result_sorted = sorted(result, key=lambda x: x[1])
        idmin, tmin = result[0]
        idmax, tmax = result[-1]
        print('min, max ', idmin, tmin,idmax, tmax  )
        print(len(same_parent), ' folders have the parent:', this_folder_id)
        for child_folder in result_sorted:
            print('down to folder/id :', child_folder[0])
            traverse3(child_folder[0])
            print('back to folder/id :', this_folder_id)
    else:
        idmin = tmin = idmax = tmax = None

    print('processing files in folder/id :', this_folder_id)
    query2 = File.select(File.id, File.file_last_modif).where(File.folder_id == this_folder_id)  #
    print(len(query2), ' files in ')
    if len(query2) > 0:
        for row_file in query2:
            print(row_file.id)
        same_parent = query2.tuples()
        if len(same_parent) > 0:
            result = [ s for  s in same_parent]
            result_sorted = sorted(result, key=lambda x: x[1])
            idmin, tmin = result[0]
            idmax, tmax = result[-1]
            print(idmin, tmin,idmax, tmax  )
        else:
            idmin = tmin = idmax = tmax = None

    Folder.update( max_files_last_modif = tmax, id_file_max_last_modif = idmax, min_files_last_modif = tmin,  id_file_min_last_modif = idmin).where(Folder.parent_folder==this_folder_id).execute()


def traverse4( this_folder_id) :

    # print('Entering in folder/id :', this_folder_id)
    query1 = Folder.select(Folder.id, Folder.folder_last_modif).where(Folder.parent_folder == this_folder_id)
    same_parent = query1.tuples()
    if len(same_parent) > 0:
        result = [ s for  s in same_parent]
        result_sorted = sorted(result, key=lambda x: x[1])
        idmin, tmin = result[0]
        idmax, tmax = result[-1]
        # print('min, max ', idmin, tmin,idmax, tmax  )
        # print(len(same_parent), ' folders have the parent:', this_folder_id)
        for child_folder in result_sorted:
            # print('down to folder/id :', child_folder[0])
            traverse4(child_folder[0])
            # print('back to folder/id :', this_folder_id)
    else:
        idmin = tmin = idmax = tmax = None

    # print('processing files in folder/id :', this_folder_id)
    query2 = File.select(File.id, File.file_last_modif).where(File.folder_id == this_folder_id)  #
    # print(len(query2), ' files in ')
    if len(query2) > 0:
        for row_file in query2:
            pass
            # print(row_file.id)
        same_parent = query2.tuples()
        if len(same_parent) > 0:
            result = [ s for  s in same_parent]
            result_sorted = sorted(result, key=lambda x: x[1])
            idmin, tmin = result[0]
            idmax, tmax = result[-1]
            # print(idmin, tmin,idmax, tmax  )
        else:
            idmin = tmin = idmax = tmax = None

    Folder.update( max_files_last_modif = tmax, id_file_max_last_modif = idmax, min_files_last_modif = tmin,  id_file_min_last_modif = idmin).where(Folder.parent_folder==this_folder_id).execute()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    root_id = 2  #

    # root_folder_inst = (Folder.select().where(Folder.id == root_id)).execute()
    # for inst in root_folder_inst:
    #     print(str(inst))

    root_folder_inst = (Folder.select().where(Folder.id == root_id)).execute()[0]
    print(str(root_folder_inst))


    # root_folder_scalar = (Folder.select().where(Folder.id == root_id)).scalar()  # -> the id

    traverse(root_id)


    exit()
