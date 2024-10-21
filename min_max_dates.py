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
ONE_INDENT = "\t"
def indents():
    global indent_level
    return indent_level*ONE_INDENT
def prindent(*args):
    print(indents(), " ".join(str(x) for x in args))
def inc_indent():
    global indent_level
    indent_level += 1
def dec_indent():
    global indent_level
    indent_level -= 1

def traverse( this_folder_id) :
    this_folder_inst = (Folder.select().where(Folder.id == this_folder_id)).execute()[0]
    prindent("Entering", repr(this_folder_inst))

    # query1 = Folder.select(fn.MIN(Folder.folder_last_modif),fn.MAX(Folder.folder_last_modif)).where(Folder.parent_folder == this_folder_id)  #
    query1 = Folder.select().where(Folder.parent_folder == this_folder_id)  #
    prindent( "Folder %s has" % str(this_folder_inst.id), len(query1), 'sub-folders')

    inc_indent()  # ------------------------------------------------------
    for row_folder in query1:
        traverse(row_folder.id)
    dec_indent()  # ------------------------------------------------------

    query2 = File.select().where(File.folder_id == this_folder_id)  #
    prindent( "Folder %s contains" % str(this_folder_inst.id), len(query2), ' files')
    inc_indent()  # ------------------------------------------------------
    for row_file in query2:
        prindent( repr(row_file))
    dec_indent()  # ------------------------------------------------------

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
    this_folder_inst = (Folder.select().where(Folder.id == this_folder_id)).execute()[0]
    prindent("Entering", repr(this_folder_inst))

    # print('processing files in folder/id :', this_folder_id)
    query2 = File.select(File.id, File.file_last_modif).where(File.folder_id == this_folder_id)  #
    prindent( "Folder %s contains" % str(this_folder_inst.id), len(query2), ' files')

    files_idmin = files_tmin = files_idmax = files_tmax = None
    if len(query2) > 0:
        # for row_file in query2:
        #     pass
        #     # print(row_file.id)
        files_in_this_folder = query2.tuples()
        if len(files_in_this_folder) > 0:
            result = [ s for  s in files_in_this_folder ]
            files_idmin, files_tmin = min(result, key=lambda x: x[1])
            files_idmax, files_tmax = max(result, key=lambda x: x[1])

            # print(idmin, tmin,idmax, tmax  )
        else:
            files_idmin = files_tmin = files_idmax = files_tmax = None

    prindent('Files : idmin: {idmin} - tmin: {tmin} -- idmax: {idmax} - tmax: {tmax}'.format( idmin= files_idmin, tmin=files_tmin, idmax=files_idmax, tmax=files_tmax ))

    query1 = Folder.select().where(Folder.parent_folder == this_folder_id)  #
    prindent( "Folder %s has" % str(this_folder_inst.id), len(query1), 'sub-folders')

    inc_indent()  # ------------------------------------------------------
    for row_folder in query1:
        traverse4(row_folder.id)
    dec_indent()  # ------------------------------------------------------

    folders_idmin = folders_tmin = folders_idmax = folders_tmax = None
    query1 = Folder.select(
        Folder.max_files_last_modif,
        Folder.id_file_max_last_modif  ,
        Folder.min_files_last_modif    ,
        Folder.id_file_min_last_modif
    ).where(Folder.parent_folder == this_folder_id)

    folders_in_this_folder = query1.tuples()
    if len(folders_in_this_folder ) > 0:

        # if this_folder_id == 2:
        #     pass

        result_min = [ (s[3], s[2]) for  s in folders_in_this_folder if (s[3] is not None and s[2] is not None)]
        result_max = [ (s[1], s[0]) for  s in folders_in_this_folder if (s[1] is not None and s[0] is not None)]

        try:
            mins = min(result_min, key=lambda x: x[1])
            folders_idmin, folders_tmin = mins[0], mins[1]
        except:
            pass

        try:
            maxs = max(result_max, key=lambda x: x[1] )
            folders_idmax, folders_tmax = maxs[0], maxs[1]
        except:
            pass
    else:
        folders_idmin = folders_tmin = folders_idmax = folders_tmax = None

    if files_tmin is None:
        if folders_tmin is None:
            mins = (None, None)
        else:
            mins = (folders_idmin, folders_tmin)
    elif folders_tmin is None:
        mins = ( files_idmin, files_tmin)
    else:
        mins = min((( files_idmin, files_tmin),(folders_idmin, folders_tmin)), key=lambda x: x[1])

    if files_tmax is None:
        if folders_tmax is None:
            maxs = (None, None)
        else:
            maxs = (folders_idmax, folders_tmax)
    elif folders_tmax is None:
        maxs = (files_idmax, files_tmax)
    else:
        maxs = max((( files_idmax, files_tmax),(folders_idmax, folders_tmax)), key=lambda x: x[1])

    Folder.update( max_files_last_modif = maxs[1], id_file_max_last_modif = maxs[0], min_files_last_modif =  mins[1],  id_file_min_last_modif = mins[0]).where(Folder.id == this_folder_id).execute()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    root_id = 2  #

    # root_folder_inst = (Folder.select().where(Folder.id == root_id)).execute()
    # for inst in root_folder_inst:
    #     print(str(inst))

    root_folder_inst = (Folder.select().where(Folder.id == root_id)).execute()[0]
    print(str(root_folder_inst))


    # root_folder_scalar = (Folder.select().where(Folder.id == root_id)).scalar()  # -> the id

    traverse4(root_id)


    exit()
