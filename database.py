### LICENSE
# This code is licensed under GPLv2. All projects using it 
# **MUST** remain open source. The code is provided 'as-is',
# so feel free to modify it as much as you like.


### IMPORTANT NOTICE
# This file is almost a 100% copy from my own bot. I've written this code a
# long time ago and am too lazy to change it. It works great, so I won't
# recommend changing it.

import sqlite3, random
import threading
db = sqlite3.connect('./data/starboard.sqlite3')
src = sqlite3.connect(':memory:')
db.backup(src)
cr = src.cursor()

def saftey(itm):
    if type(itm) == str:
        return f'"{itm}"'
    elif itm == None:
        return 'NULL'
    return itm

def save():
    src.commit()
    with db:
        src.backup(db)
        db.commit()
        db.backup(src)
        src.commit()

save_timer = None
def timeout_save():
    global save_timer
    try:
        save_timer.cancel()
    except:
        pass
    save_timer = threading.Timer(5, save) # basically window.setTimeout(save, 5000)
    save_timer.start()

def kwarg(**kwargs):
    if len(kwargs):
        return 'WHERE '+' and '.join(f'{saftey(k)} {"is" if saftey(kwargs[k]) == "NULL" else "="} {saftey(kwargs[k])}' for k in kwargs)
    return ''

def arg(*args):
    args = [str(saftey(itm)) for itm in args]
    return ', '.join(args)

def read_db(command, *args):
    #print(command, *args)
    if len(args):
        cr.execute(command, tuple(args))
    else:
        cr.execute(command)
    timeout_save()
    return cr

def commit(command, *args):
    #print(command, *args)
    cr = read_db(command, *args)

def retrieve(command, *args):
    #print(command, *args)
    cr = read_db(command, *args)
    return cr.fetchall()

def get(table, *names, return_first = True, is_not_null = [],
        return_null = False, return_as_list = False, rtn = None,
        **kwargs):
    cols, where = arg(*names), kwarg(**kwargs)
    not_null = ' and '.join(f'{x} IS NOT NULL' for x in is_not_null)
    selected = retrieve(f'SELECT {cols} FROM {table} {where} {"WHERE" if not_null and not where else " and " if where and not_null else ""} {not_null}')
    returned = None
    if not return_first:
        return rtn(selected) if rtn != None else selected
    elif selected in [[],None,[None]]:
        returned = None if return_null else []
    elif len(selected) == 1:
        if len(selected[0]) == 1 and not return_as_list:
            returned = selected[0][0] # One item found
        else:
            returned = list(selected[0])  # Many items but one group
    elif all(len(a)==1 for a in selected):
        returned = [a[0] for a in selected] # Many groups with one item
    else:
        returned = selected # Just in case
    if rtn in [int, str, list, dict, float, tuple, bytes,
               complex, frozenset, bytearray, object, set,
               bool, range, memoryview, type]: #Basic returns only
        return rtn(returned)
    else:
        return returned

def addCol(table, name, param = ''):
    commit(f'ALTER TABLE {table} ADD COLUMN "{name}" {param}')

def delCol(table, *names):
    for name in names:
        commit(f'ALTER TABLE {table} DROP COLUMN "{name}"')

def newTab(name, *args):
    commit(f'CREATE TABLE {name}(id INTEGER UNIQUE NOT NULL {", "+arg(args) if len(args) else ""})')

def delTab(*names):
    for name in names:
        commit(f'DROP TABLE {name}')

def renTab(table, new):
    commit(f'ALTER TABLE {table} RENAME TO {new}')

def renCol(table, col, new):
    commit(f'ALTER TABLE {table} RENAME COLUMN {col} TO {new}')

def getTabs():
    return get('sqlite_master', 'name', type="table")

def getCols(table):
    return [a[1] for a in read_db(f'PRAGMA table_info({table})').fetchall()[1:]]

def update(table, col, val, **kwargs):
    where = kwarg(**kwargs)
    commit(f'UPDATE {table} SET "{col}" = ? {where}', val)

def remove(table, **kwargs):
    where = kwarg(**kwargs)
    commit(f'DELETE FROM {table} {where}')

def insert(table, **kwargs):
    if len(kwargs) > 0:
        commit(f'INSERT INTO {table}({arg(*list(kwargs))}) VALUES({arg(*kwargs.values())})')
