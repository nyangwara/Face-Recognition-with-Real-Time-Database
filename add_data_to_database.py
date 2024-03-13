import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("face-attendance-realtime-service-acc-key.json")
#print(cred)  # Add this line to print the credential object
firebase_admin.initialize_app(cred,{
    'databaseURL':""
})

ref = db.reference('Students')
data={
    "234234":{
        "Name":"Sayyid Mogaka",
        "Major":"Applied Informatics",
        "starting Year":2017,
        "total attendance":5,
        "standing":"G",
        "Year":3,
        "last_attendance_time":"2024-01-29 12:30:45"
    },
    "1232132": {
        "Name": "Michelle Alozie",
        "Major": "Molecular Biology",
        "starting Year": 2021,
        "total attendance": 12,
        "standing": "G",
        "Year": 5,
        "last_attendance_time": "2024-01-29 12:30:45"
    },
    "12432483": {
        "Name": "SaM Kerr",
        "Major": "Nutrition",
        "starting Year": 2022,
        "total attendance": 12,
        "standing": "G",
        "Year": 2,
        "last_attendance_time": "2023-12-12 08:30:45"
    },
    "788345934": {
        "Name": "Peter Salasya",
        "Major": "Political Science",
        "starting Year": 2020,
        "total attendance": 4,
        "standing": "B",
        "Year": 4,
        "last_attendance_time": "2023-11-29 11:30:45"
    }
}

for key,value in data.items():
    ref.child(key).set(value) #send data to a specific directory ,with set it take the key and value
