"""
Interface to the database.
"""

import mysql.connector
import logging
from datetime import datetime
from datetime import timezone




####################################################################################################################
#
# API
#
####################################################################################################################

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



def update_road_event(mydb, re, is_new=True):
    '''
    Update or add new road event to the database.

    :param mydb: DB connector object.
    :param re: GeoJSON WZDx-formatted dictionary with road event info.
    '''

    mycursor = mydb.cursor()

    geom_val = "ST_GeomFromText('{}(".format(re['geometry']['type'].upper())
    coords = re['geometry']['coordinates']
    s = ""
    for p in coords:
        geom_val += "{}{} {}".format(s, p[0], p[1])
        s = ", "
    geom_val += ")')"

    sql = "UPDATE road_event_feature SET geometry={} WHERE id='{}'".format(geom_val, re['id'])
    if is_new:
        sql = "INSERT INTO road_event_feature VALUES('{}',{},DEFAULT)".format(re['id'], geom_val)

    try:
        mycursor.execute(sql)
    except Exception as e:
        logging.error("update_road_event(): SQL: {} ; Error: {}".format(sql, str(e)))
        logging.error("update_road_event(): Failed to update core details for road event ID: {}".format(re_id))

    update_work_zone_event(mycursor, re)
    update_core_details(mycursor, re)
    update_lanes(mycursor, re)
    update_type_of_work(mycursor, re)
    update_worker_presence(mycursor, re)

    mydb.commit()
    
    return





####################################################################################################################
#
# Auxiliary Functions
#
####################################################################################################################

def update_work_zone_event(mycursor, re):
    '''
    Insert or update the work zone event info.

    :param mycursor: Cursor for SQL execution.
    :param re: GeoJSON WZDx-formatted dictionary with road event info.
    '''

    re_id = re['id']
    sql = "DELETE FROM work_zone_event WHERE road_event_feature_id='{}'".format(re_id)
    mycursor.execute(sql)

    pr = re['properties']

    start_date, end_date = dt_str2sql_comp(pr['start_date']), dt_str2sql_comp(pr['end_date'])

    sd_verified = "DEFAULT"
    k = "start_date_accuracy"
    if k in pr.keys():
        sd_verified = "TRUE" if pr[k] == "verified" else "FALSE"
    
    ed_verified = "DEFAULT"
    k = "end_date_accuracy"
    if k in pr.keys():
        ed_verified = "TRUE" if pr[k] == "verified" else "FALSE"

    sp_verified = "DEFAULT"
    k = "beginning_accuracy"
    if k in pr.keys():
        sp_verified = "TRUE" if pr[k] == "verified" else "FALSE"

    ep_verified = "DEFAULT"
    k = "ending_accuracy"
    if k in pr.keys():
        ep_verified = "TRUE" if pr[k] == "verified" else "FALSE"

    wz_type = "DEFAULT"
    k = "work_zone_type"
    if k in pr.keys():
        wz_type = "'" + pr[k] + "'"

    location_method = "DEFAULT"
    k = "location_method"
    if k in pr.keys():
        location_method = "'" + pr[k] + "'"
    
    vehicle_impact = "DEFAULT"
    k = "vehicle_impact"
    if k in pr.keys():
        vehicle_impact = "'" + pr[k] + "'"

    b_cross_street = "DEFAULT"
    k = "beginning_cross_street"
    if k in pr.keys():
        b_cross_street = "'" + pr[k].replace("'", "\\'") + "'"

    e_cross_street = "DEFAULT"
    k = "ending_cross_street"
    if k in pr.keys():
        e_cross_street = "'" + pr[k].replace("'", "\\'") + "'"
    
    b_milepost = "DEFAULT"
    k = "beginning_milepost"
    if k in pr.keys():
        b_milepost = pr[k]
    
    e_milepost = "DEFAULT"
    k = "ending_milepost"
    if k in pr.keys():
        e_milepost = pr[k]
    
    reduced_speed_limit = "DEFAULT"
    k = "reduced_speed_limit_kph"
    if k in pr.keys():
        reduced_speed_limit = pr[k]
    
    sql = "INSERT INTO work_zone_event VALUES('{}','{}','{}',{},{}, {},{},{},{},{}, {},{},{},{},{})".format(
        re_id, start_date, end_date, sd_verified, ed_verified, sp_verified, ep_verified, wz_type, location_method, vehicle_impact,
        b_cross_street, e_cross_street, b_milepost, e_milepost, reduced_speed_limit
    )
    try:
        mycursor.execute(sql)
    except Exception as e:
        logging.error("update_work_zone_event(): SQL: {} ; Error: {}".format(sql, str(e)))
        logging.error("update_work_zone_event(): Failed to update core details for road event ID: {}".format(re_id))

    return



def update_core_details(mycursor, re):
    '''
    Insert or update the road event core details.

    :param mycursor: Cursor for SQL execution.
    :param re: GeoJSON WZDx-formatted dictionary with road event info.
    '''

    re_id = re['id']
    sql = "DELETE FROM road_event_core_details WHERE road_event_feature_id='{}'".format(re_id)
    mycursor.execute(sql)

    k = "core_details"
    if k not in re['properties'].keys():
        logging.error("update_core_details(): Core details are missing in the road event dictionary.")
        return
    
    cd = re['properties'][k]

    e_type = "work-zone"
    k = "event_type"
    if k in cd.keys():
        e_type = cd[k]
    
    ds_id = " "
    k = "data_source_id"
    if k in cd.keys():
        ds_id = cd[k]

    r_names = ""
    sep = ""
    k = "road_names"
    if k in cd.keys():
        road_names = cd[k]
        for rn in road_names:
            r_names += sep + rn.replace("'", "\\'")
            sep = ";"
    
    direction = "unknown"
    k = "direction"
    if k in cd.keys():
        direction = cd[k]

    name = "DEFAULT"
    k = "name"
    if k in cd.keys():
        name = "'" + cd[k].replace("'", "\\'") + "'"
     
    description = "DEFAULT"
    k = "description"
    if k in cd.keys():
        description = "'" + cd[k].replace("'", "\\'") + "'"

    created = "DEFAULT"
    k = "creation_date"
    if k in cd.keys():
        created = "'" + dt_str2sql_comp(cd[k]) + "'"

    updated = "DEFAULT"
    k = "update_date"
    if k in cd.keys():
        updated = "'" + dt_str2sql_comp(cd[k]) + "'"

    sql = "INSERT INTO road_event_core_details VALUES('{}','{}','{}','{}','{}', {},{},{},{})".format(
        re_id, e_type, ds_id, r_names, direction, name, description, created, updated
    )
    try:
        mycursor.execute(sql)
    except Exception as e:
        logging.error("update_core_details(): SQL: {} ; Error: {}".format(sql, str(e)))
        logging.error("update_core_details(): Failed to update core details for road event ID: {}".format(re_id))

    return



def update_lanes(mycursor, re):
    '''
    Insert or update the lane info.

    :param mycursor: Cursor for SQL execution.
    :param re: GeoJSON WZDx-formatted dictionary with road event info.
    '''

    re_id = re['id']
    sql = "DELETE FROM lane WHERE road_event_feature_id='{}'".format(re_id)
    mycursor.execute(sql)

    k = "lanes"
    if k not in re['properties'].keys():
        logging.debug("update_lanes(): Lane info is missing in the road event dictionary.")
        return

    lanes = re['properties'][k]

    for li in lanes:
        order = "DEFAULT"
        k = "order"
        if k in li.keys():
            order = li[k]

        l_type = "DEFAULT"
        k = "type"
        if k in li.keys():
            l_type = "'" + li[k] + "'"

        status = "DEFAULT"
        k = "status"
        if k in li.keys():
            status = "'" + li[k] + "'"

        sql = "INSERT INTO lane VALUES('{}',{},{},{})".format(re_id, order, l_type, status)
        try:
            mycursor.execute(sql)
        except Exception as e:
            logging.error("update_lanes(): SQL: {} ; Error: {}".format(sql, str(e)))
            logging.error("update_lanes(): Failed to update core details for road event ID: {}".format(re_id))

    return



def update_type_of_work(mycursor, re):
    '''
    Insert or update the types of work info.

    :param mycursor: Cursor for SQL execution.
    :param re: GeoJSON WZDx-formatted dictionary with road event info.
    '''

    re_id = re['id']
    sql = "DELETE FROM type_of_work WHERE road_event_feature_id='{}'".format(re_id)
    mycursor.execute(sql)

    k = "types_of_work"
    if k not in re['properties'].keys():
        logging.debug("update_type_of_work(): Types of work info is missing in the road event dictionary.")
        return

    tows = re['properties'][k]

    for tow in tows:
        tn = "DEFAULT"
        k = "type_name"
        if k in tow.keys():
            tn = "'" + tow[k] + "'"

        iac = "DEFAULT"
        k = "is_architectural_change"
        if k in tow.keys():
            iac = tow[k]

        sql = "INSERT INTO type_of_work VALUES('{}',{},{})".format(re_id, tn, iac)
        try:
            mycursor.execute(sql)
        except Exception as e:
            logging.error("update_type_of_work(): SQL: {} ; Error: {}".format(sql, str(e)))
            logging.error("update_type_of_work(): Failed to update core details for road event ID: {}".format(re_id))

    return



def update_worker_presence(mycursor, re):
    '''
    Insert or update the worker presence info.

    :param mycursor: Cursor for SQL execution.
    :param re: GeoJSON WZDx-formatted dictionary with road event info.
    '''

    re_id = re['id']
    sql = "DELETE FROM worker_presence WHERE road_event_feature_id='{}'".format(re_id)
    mycursor.execute(sql)

    k = "worker_presence"
    if k not in re['properties'].keys():
        logging.debug("update_worker_presence(): Worker presence info is missing in the road event dictionary.")
        return
    
    wp = re['properties'][k]

    awp = "DEFAULT"
    k = "are_workers_present"
    if k in wp.keys():
        awp = wp[k]
    
    definition = "DEFAULT"
    k = "definition"
    if k in wp.keys():
        defs = wp[k]
        s  = ""
        definition = "'"
        for df in defs:
            definition += s + df
            s = ";"
        definition += "'"
    
    method = "DEFAULT"
    k = "method"
    if k in wp.keys():
        method = "'" + wp[k] + "'"
    
    last_confirmed = "DEFAULT"
    k = "worker_presence_last_confirmed_date"
    if k in wp.keys():
        last_confirmed = "'" + dt_str2sql_comp(wp[k]) + "'"
    
    confidence = "DEFAULT"
    k = "confidence"
    if k in wp.keys():
        confidence = "'" + wp[k] + "'"

    sql = "INSERT INTO worker_presence VALUES('{}',{}, {},{},{},{})".format(
        re_id, awp, definition, method, last_confirmed, confidence
    )
    try:
        mycursor.execute(sql)
    except Exception as e:
        logging.error("update_worker_presence(): SQL: {} ; Error: {}".format(sql, str(e)))
        logging.error("update_worker_presence(): Failed to update core details for road event ID: {}".format(re_id))


    return


def dt_str2sql_comp(dt_str):
    '''
    Convert date-time string to SQL compatible format.

    :param dt_str: Date-time string.

    :return: SQL-compatible date-time string.
    '''
    dt = dt_str[:-1]
    parts = dt.split("T")
    res = parts[0] + " " + parts[1]
    #d = datetime.fromisoformat(dt)
    #res = d.strftime('%Y-%m-%d %H:%M:%S')

    return res