from flask import Flask, render_template,request
import json
from flask_pymongo import PyMongo
from pymongo import message
import pymongo
from datetime import datetime,date
import urllib.request

app = Flask(__name__)
mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/schedulardb")
db = mongodb_client.db
api = '424b66ac00e8889a485863936ec601a2'
city = 'Mumbai'
source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q='+city+'&units=metric&appid='+api).read()
list_of_data = json.loads(source)
weatherData = {
       
        "weather": list_of_data['weather'][0]['main'],
        "weather_des": list_of_data['weather'][0]['description'],
        "temp": list_of_data['main']['temp'],
        "feels_like":list_of_data['main']['feels_like'], 
        "weatherIcon": list_of_data['weather'][0]['icon']
    }
class Item:
  def __init__(self, vals):
    self.__dict__ = vals



@app.route('/')
def index():
   return render_template('index.html')

@app.route('/calendarPage')
def calendar_page():
   
   e01 = list(db.schedulardb.find())
   print(e01)
   print(type(e01))
   e02 = [{k: v for k, v in d.items() if k != '_id'} for d in e01] #remove the _id key-value from extracted document
   today = date.today()
   e03 = [a_dict['end'] for a_dict in e02]
   for i in e03:
      di = datetime.strptime(i, "%Y-%m-%d").date()
      if today>di:
         db.schedulardb.delete_one({'end':i})
   
   # db.schedulardb.find().sort('{}'.format('title'), 1)

   doc = db.schedulardb.find().sort([("end", 1), ("endTime", 1)])
 #
   print("----------------------------------------------------------------------------------------------------------------------")
   for x in doc:
      print(x)

   e1 = list(db.schedulardb.find().sort([("end", 1), ("endTime", 1),("startTime",1)]))   # Sorting the collection from database.
   # print(e1)
   # print(type(e1))
   e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1]

  

   # print(e2)
   even = len(e2)
   # print(even)

   return render_template('calendar_page.html',events = e2,n = even, data = [Item(i) for i in e2],weatherData = weatherData)

@app.route('/getdata', methods=['GET','POST'])
def data_get():
   if request.method == "POST":
         requestInput = request.form
         eventDate = requestInput.get('dt') 
         eventName = requestInput.get('name')
         eventDes = requestInput.get('content1')
         # eventType = requestInput.get('optradio')
         eventSt = requestInput.get('stTime')
         print(type(eventSt))
         eventEnd = requestInput.get('endTime')
         endDate= datetime.strptime(requestInput.get('enddate_'), "%Y-%m-%d")    # converting the normal date to YYYY-MM-DD hh:mm:ss
         str_endate=str(endDate)                  # converting the date into string 
         str_endate=str_endate[0:10]              # extracting the date part only from the string  i.e YYYY-MM-DD
         print("endate -> "+str_endate)           # printing the date part
         

         def timeConvert(s):  #converts 12hr format time to 24hr format time
            m2 = s
            in_time = datetime.strptime(m2, "%I:%M %p")
            convertTime = datetime.strftime(in_time, "%H:%M")
            return convertTime
         
         startTime = (timeConvert(eventSt))
         endTime = (timeConvert(eventEnd))
         
         
         
         if(len(eventName)>0):
            
            db.schedulardb.insert_one({'start':eventDate, 'title':eventName, 'des': eventDes, 'startTime': startTime, 'stTimeap':eventSt ,'endTime': endTime, 'endTimeap':eventEnd, 'end': str_endate })
            
            print("insert running")
            # db.schedulardb.find().sort('start',PyMongo.ASCENDING)
            e1 = list(db.schedulardb.find().sort([("end", 1), ("endTime", 1),("startTime",1)]))
            print(e1)
            print(type(e1))
            e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1] #remove the _id key-value from extracted document
            print(e2)
            even = len(e2)
            print(even)


   return render_template('/calendar_page.html',events = e2,n = even, data = [Item(i) for i in e2],weatherData = weatherData)

@app.route('/deleteData', methods=['GET','POST'])
def data_del():
   if request.method == "POST":
         requestInput = request.form
         startDate = requestInput.get('stdate_')                # Getting the date from js
         eTitle = requestInput.get('title_')   
         startTime = requestInput.get('stTime_')           # Getting the title from js
         endTime = requestInput.get('eTime_')
         endDate = requestInput.get('eDate_')
         print(startDate+" "+eTitle+" "+startTime+" "+endTime+" "+endDate)
       
         # print(even)
         # formateDate = new SimpleDateFormat("MM-dd-yyyy").format(date)
         # formate_date=eventDate.strftime("%H:%M:%SZ")
         # print(eventDate)

         myquery = {'start':startDate,'title': eTitle, 'startTime': startTime, 'endTime':endTime,'end':endDate}

         db.schedulardb.delete_one(myquery)
         e1 = list(db.schedulardb.find().sort([("end", 1), ("endTime", 1),("startTime",1)]))
         # print(e1)
         # print(type(e1))
         e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1]
         even = len(e2)
         print("Event deleted")
   return render_template('/calendar_page.html',events = e2,n = even, data = [Item(i) for i in e2],weatherData = weatherData)


if __name__ == '__main__':
   app.run(debug = True)