"""
Work Zone Data Collector that polls SF 511.org.
Data stream contains WZDx v4.1.
"""

import requests
import logging
import re
import json
import db_routines as dbr



#logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

src_url = "https://api.511.org/traffic/wzdx?api_key=789a13cf-d2e0-46db-95f2-54c2611933c1"



def get_wz_update(url):
    '''
    Call to the 511.org API and return a dictionary with the current WZ data.

    :param url: URL ponting to WZDx API of 511.org including the API key.
    
    :return: Dictionary with WZ road events. 
    '''

    failure = True
    cnt = 0
    r = None

    while failure:
        try:
            rsp = requests.get(url)
            r = rsp.json()
            failure = False
            if cnt > 0:
                logging.info("Connected to 511.org after {} failed attempt(s).".format(cnt))
            logging.info("Downloaded {} road events from 511.org.".format(len(r['features'])))
        except:
            cnt += 1
            max_failures = 10
            if cnt > max_failures:
                logging.error("Quitting after {} failed attempts to onnect to 511.org.".format(max_failures))
                return None

    return r



def update_wz_info_in_db(mydb, features, re_ids):
    '''
    Insert new road events into the database and update the existing ones.

    :param mydb: DB connector object.
    :param features: List of GeoJSON WZDx-formatted features with road event info.
    :param re_ids: Set of road event IDs.

    :return: Updated set of road event IDs - the ones that absent from the 511.org feed.
    '''

    acnt, ucnt = 0, 0
    for f in features:
        if f['id'] in re_ids:
            ucnt += 1
            re_ids.remove(f['id'])
            logging.debug("{}) {}: Updated.".format(ucnt, f['id']))
        else:
            acnt += 1
            dbr.insert_new_road_event(mydb, f)
            logging.debug("{}) {}: Added.".format(acnt, f['id']))

    logging.info("Updated {} road events and added {} road events.".format(ucnt, acnt))

    return re_ids



def mark_road_events_for_deletion(mydb, re_ids):
    '''
    Mark road events with IDs from the given set as deleted.

    :param mydb: DB connector object.
    :param re_ids: Set of road event IDs.    
    '''

    cnt = 0
    for reid in re_ids:
        cnt += 1
        dbr.mark_road_event_as_deleted(mydb, reid)
        logging.debug("{}) {}: Marked for deletion.".format(cnt, reid))
    
    logging.info("Marked {} road events for deletion.".format(cnt))

    return






#==============================================================================
# Main function - for standalone execution.
#==============================================================================

def main(argv):
    global src_url

    mydb = dbr.connect()
    dbr.delete_marked_road_events_older_than(mydb, spec="2 HOUR")
    re_ids = dbr.select_road_event_ids(mydb, filter={'exclude_deleted': True})

    r = get_wz_update(src_url)
    if r == None:
        return
    
    features = r['features']
    feed_info = r['road_event_feed_info']

    re_ids = update_wz_info_in_db(mydb, features, re_ids)
    mark_road_events_for_deletion(mydb, re_ids)

    mydb.close()



if __name__ == "__main__":
    main(None)