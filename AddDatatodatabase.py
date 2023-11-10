import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://attendence-system-8e085-default-rtdb.firebaseio.com/'
})


ref=db.reference('Students')
data={
    "321654":
        {
            "Name":"Simran kaur ",
            "Branch":"Cse",
            "starting_year":2022,
            "total_attendence":8,
            "standing":"G",
            "year":3,
            "last_attendence_time":"2023-10-18  00:54:34"

        },
    "852741":
        {
            "Name": "Gourav Batar  ",
            "Branch": "CSE",
            "starting_year": 2022,
            "total_attendence": 9,
            "standing": "G",
            "year": 3,
            "last_attendence_time": "2023-10-18  00:54:34"

        },
    "963852":
        {
            "Name": "Siya Jindal ",
            "Branch": "Cse",
            "starting_year": 2022,
            "total_attendence": 10,
            "standing": "G",
            "year": 3,
            "last_attendence_time": "2023-10-18  00:54:34"

        }

}
for key,value in data.items():
    ref.child(key).set(value)