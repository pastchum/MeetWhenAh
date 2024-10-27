import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from google.cloud.firestore_v1.base_query import FieldFilter

import json
from datetime import datetime
from icecream import ic


cred = credentials.Certificate("meetwhenbot-firebase-adminsdk-gi7ng-23bb4de9f9.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def setEntry(col, data): #ref is a file path. data is python dict
    #data = json.dumps(data, indent=2, sort_keys=True, default=str)
    db.collection(col).add(data)

def getEntry(col, field, value, field2=None, value2=None): #col is the collection, whereas field is the data field that fits
    ref = db.collection(col)
    if field2 == None or value2 == None or (field2 == None and value2 == None): #if there is only one set of values to query
        query_ref = ref.where(filter=FieldFilter(field, "==", value))
    else:
        query_ref = ref.where(filter=FieldFilter(field, "==", value)).where(filter=FieldFilter(field2, "==", value2))
 
    for doc in query_ref.stream():
        return doc

def updateEntry(doc, field, value):
    doc.reference.update({
        field: value
    })

"""
data = {
    "group_id" : "21039",
    "members" : ["123123", "51248124", "4124124"],
    "dates_chosen" : [datetime.now(), datetime.now()],
    "event_name" : "test_event",
    "hours occupied": { str(i): [] for i in range(25) },
    "timeout": datetime.now()
    "inline_message_id" : "123123"
}
"""