from flask import Flask, render_template,request,jsonify,json
from flask_pymongo import PyMongo
from pymongo import message
from datetime import datetime

app = Flask(__name__)
mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/schedulardb")
db = mongodb_client.db

class Item:
  def __init__(self, vals):
    self.__dict__ = vals



@app.route('/')
def index():
   return render_template('index.html')

@app.route('/calendarPage')
def calendar_page():
   
   e1 = list(db.schedulardb.find())
   print(e1)
   print(type(e1))
   e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1] #remove the _id key-value from extracted document
   print(e2)
   even = len(e2)
   print(even)

   return render_template('calendar_page.html',events = e2,n = even, data = [Item(i) for i in e2])

@app.route('/getdata', methods=['GET','POST'])
def data_get():
   if request.method == "POST":
         requestInput = request.form
         eventDate = requestInput.get('dt') 
         eventName = requestInput.get('name')
         eventDes = requestInput.get('content1')
         # eventType = requestInput.get('optradio')
         eventSt = requestInput.get('stTime')
         eventEnd = requestInput.get('endTime')

         def timeConvert(s):  #converts 12hr format time to 24hr format time
            m2 = s
            in_time = datetime.strptime(m2, "%I:%M %p")
            convertTime = datetime.strftime(in_time, "%H:%M")
            return convertTime
         
         startTime = (timeConvert(eventSt))
         endTime = (timeConvert(eventEnd))
         

         
         if(len(eventName)>0):
            db.schedulardb.insert_one({'start':eventDate, 'title':eventName, 'des': eventDes, 'startTime': startTime, 'stTimeap':eventSt ,'endTime': endTime, 'endTimeap':eventEnd })
            print("insert running")
            
            e1 = list(db.schedulardb.find())
            print(e1)
            print(type(e1))
            e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1] #remove the _id key-value from extracted document
            print(e2)
            even = len(e2)
            print(even)


   return render_template('/calendar_page.html',events = e2,n = even, data = [Item(i) for i in e2])

@app.route('/deleteData', methods=['GET','POST'])
def data_del():
   if request.method == "POST":
         requestInput = request.form
         eventDate = requestInput.get('date_')                # Getting the date from js
         eventTitle = requestInput.get('title_')              # Getting the title from js
         print(eventDate+" "+eventTitle)
       
         # print(even)
         myquery = { 'start':eventDate,'title': eventTitle }

         db.schedulardb.delete_one(myquery)
         e1 = list(db.schedulardb.find())
         # print(e1)
         # print(type(e1))
         e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1]
         even = len(e2)
         print("Event deleted")
   return render_template('/calendar_page.html',events = e2,n = even, data = [Item(i) for i in e2])


if __name__ == '__main__':
   app.run(debug = True)