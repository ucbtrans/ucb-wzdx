"""
Interface to the database.
"""

import mysql.connector



def connect(): 
    '''
    Connect to the database.

    :return: DB connector object.
    '''

    host = 'localhost'
    port = 3306
    user = 'root'
    password = 'WZDx24'
    database = 'wzdb'

    conn = mysql.connector.connect(host=host, port=port, database=database, user=user, password=password)

    return conn



def select_road_event_ids(mydb, filter=None):
    '''
    Select the IDs of all undeleted road events subject to a given filter.

    :param mydb: DB connector object.
    :param filter: Dictionary describing the selection parameters.

    :return: Set of road event IDs.
    '''

    sql = "SELECT id FROM road_event_feature"

    if filter != None and isinstance(filter, dict):
        key = 'exclude_deleted'
        if key in filter.keys() and filter[key]:
            sql += " WHERE deleted is null"

    mycursor = mydb.cursor()
    mycursor.execute(sql)
    records = mycursor.fetchall()
    mydb.commit()

    re_ids = set()
    for r in records:
        re_ids.add(r[0])

    return re_ids



def mark_road_event_as_deleted(mydb, re_id):
    '''
    Mark the record for the given road event ID as deleted.

    :param mydb: DB connector object.
    :param re_id: Road event ID.
    '''

    sql = "UPDATE road_event_feature SET deleted=now() WHERE id='{}'".format(re_id)
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()

    return



def delete_road_event(mydb, re_id):
    '''
    Delete the record for the given road event ID.

    :param mydb: DB connector object.
    :param re_id: Road event ID.
    '''

    sql = "DELETE FROM road_event_feature WHERE id='{}'".format(re_id)
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()

    return



def delete_marked_road_events_older_than(mydb, spec="7 DAY"):
    '''
    Delete road event records that were marked as deleted earlier than now minus specified interval.

    :param mydb: DB connector object.
    :param spec: Specified interval, e.g., "3 MONTH", "7 DAY", "72 HOUR".
    '''

    sql = "DELETE FROM road_event_feature WHERE deleted < now() - INTERVAL {}".format(spec)
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()

    return



def insert_new_road_event(mydb, re):
    '''
    Add new road event to the database.

    :param mydb: DB connector object.
    :param re: GeoJSON WZDx-formatted dictionary with road event info.
    '''

    mycursor = mydb.cursor()

    sql = "INSERT INTO road_event_feature VALUES('{}', ST_GeomFromText('{}(".format(re['id'], re['geometry']['type'].upper())
    coords = re['geometry']['coordinates']
    s = ""
    for p in coords:
        sql += "{}{} {}".format(s, p[0], p[1])
        s = ", "
    sql += ")'), null)"  
    mycursor.execute(sql)


    mydb.commit()
    
    return



