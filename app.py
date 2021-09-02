
from flask import Flask, render_template,request,session,url_for
import json
from flask_pymongo import PyMongo
from pymongo import message
import pymongo
from datetime import datetime,date,timedelta
import urllib.request
from flask_mail import Mail, Message
from werkzeug.utils import redirect
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config['SECRET_KEY'] = 'secretKey'
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mail = Mail(app) # instantiate the mail class
   
# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'schedularxp@gmail.com'
app.config['MAIL_PASSWORD'] = 'Sch3dular_Xp'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/schedulardb") 
db = mongodb_client.db

def weather(city):
   api = '424b66ac00e8889a485863936ec601a2'
   city =  city
   source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q='+city+'&units=metric&appid='+api).read()
   list_of_data = json.loads(source)
   weatherData = {
         
         "weather": list_of_data['weather'][0]['main'],
         "weather_des": list_of_data['weather'][0]['description'],
         "temp": list_of_data['main']['temp'],
         "feels_like":list_of_data['main']['feels_like'], 
         "weatherIcon": list_of_data['weather'][0]['icon']
      }
   return weatherData
class Item:
  def __init__(self, vals):
    self.__dict__ = vals



@app.route('/')
def index():
   return render_template('page_1.html')


@app.route('/Signup')
def SignUp():
   return render_template('Signup.html')

@app.route('/valid', methods=['GET','POST'])
def validate():

   if request.method == "POST":
         requestInput = request.form
         em = requestInput.get("emailId")
         print(em)
         ctr = requestInput.get("city")
         print(ctr)
         p1 = requestInput.get("password1")
         print(p1)
         p2 = requestInput.get("password2")
         print(p2)
         if(p1==p2):
            l1 = list(db.schedulardb.find({'username':em}))
            if(l1==[]):
               

               db.schedulardb.insert_one({'username':em, 'password': p1, 'city': ctr })

               return render_template('Login.html')
            else:
               return render_template('Signup.html',flag="False")
         else:
            return render_template('Signup.html')

@app.route('/Login')
def Login():
   return render_template('Login.html')
   

@app.route('/LoginVal', methods=['GET','POST'])
def loginVal():
   flag =True
   if request.method == "POST":
      requestInput = request.form
      un = requestInput.get("username")
      
      passwd = requestInput.get("pass")
      
      a = list(db.schedulardb.find({'username':un, 'password':passwd}))
      if(a!=[]):
         session['ct'] = a[0].get('city')
         city = a[0].get('city')
         session['emailid'] = a[0].get('username')
         session['ps'] = a[0].get('password')

         return redirect(url_for('calendar_page'))
      
      
      # print("doesnt exist")
      
      flag=False
      return render_template('Login.html',flag=flag)
      

@app.route('/calendarPage')
def calendar_page():
   
   # e01 = list(db.schedulardb.find())
   un = session.get('emailid')
   ps = session.get('ps')
   ct = session.get('ct')
   
   e01 = list(db.schedulardb.find({'username':un, 'password':ps}))
   e011 = list(db.schedulardb.find({'username':un, 'password':ps,'start': {"$exists": True}}))
   print(e011)
   
   print(e01)
   print(type(e01))
   if(e011!=[]):
      print("in if")
      e02 = [{k: v for k, v in d.items() if k != '_id'} for d in e01] #remove the _id key-value from extracted document
      today = date.today()
      e033 = e02[1:]
      e03 = [a_dict['end'] for a_dict in e033]
      for i in e03:
         di = datetime.strptime(i, "%Y-%m-%d").date()
         if today>di:
            db.schedulardb.delete_one({'end':i})
      
      # db.schedulardb.find().sort('{}'.format('title'), 1)

      # doc = db.schedulardb.find({'username':un, 'password':ps}).sort([("end", 1), ("endTime", 1)])
   #
      print("----------------------------------------------------------------------------------------------------------------------")
      
        

      e1 = list(db.schedulardb.find({'username':un, 'password':ps}).sort([("end", 1), ("endTime", 1),("startTime",1)]))   # Sorting the collection from database.
      
      # print(type(e1))
      e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1]
      e22 = e2[1:]

      now = datetime.now() 
      remindTime1 = now.strftime("%Y-%m-%d %H:%M")
      remindTime = datetime.strptime(remindTime1,"%Y-%m-%d %H:%M") #current date and time
      

      for k in e22:

         eve_time1 = k.get('end')+" "+k.get('endTime') 
         eve_time = datetime.strptime(eve_time1,"%Y-%m-%d %H:%M")
         eveTime_early = eve_time - timedelta(hours=2) #time and date of event with earliest endtime
         print(type(remindTime))
         print(type(eve_time))

         if(k.get('sentMail')==0):
            print("inside if 1")
            if(remindTime>=eveTime_early):
               # tempEve = e1[0].get('title')
               print("inside if 2")

               print(mail)
               msg = Message(
                           k.get('title')+' deadline creeping up!',
                           sender ='schedularxp@gmail.com',
                           recipients = [un]
                           )
               msg.body = 'Deadline for '+k.get('title')+' is due on '+k.get('end')+' at '+k.get('endTimeap')
               mail.send(msg)

               # print(e2)
         
               # print(even)

               # newvalues = { "$set": { "sentMail": 1} }
               # query = { "sentMail": 0,'username':un, 'password':ps }

               db.schedulardb.update_one({ "sentMail": 0}, { "$set": { "sentMail": 1} })
      even = len(e22)

      weatherData = weather(ct)
      print('e22:-------   ',e22)
      return render_template('calendar_page.html',events = e22,n = even, data = [Item(i) for i in e22],weatherData = weatherData)
         #return render_template('calendar_page.html',events = [],n = 0, data = [],weatherData = weatherData)


   weatherData = weather(ct)
   return render_template('calendar_page.html',events = [],n = 0, data = [],weatherData = weatherData)

@app.route('/getdata', methods=['GET','POST'])
def data_get():
   un = session.get('emailid')
   ps = session.get('ps')
   ct = session.get('ct')

   if request.method == "POST":
         requestInput = request.form
         eventDate = requestInput.get('dt') 
         eventName = requestInput.get('event_name')
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
            
            db.schedulardb.insert_one({'username':un, 'password':ps,'start':eventDate, 'title':eventName, 'des': eventDes, 'startTime': startTime, 'stTimeap':eventSt ,'endTime': endTime, 'endTimeap':eventEnd, 'end': str_endate, 'sentMail': 0 })
            
            print("insert running")
            # db.schedulardb.find().sort('start',PyMongo.ASCENDING)
            e1 = list(db.schedulardb.find({'username':un, 'password':ps}).sort([("end", 1), ("endTime", 1),("startTime",1)]))
            print(e1)
            
            # e22 = [{k: v for k, v in d.items() if k != 'username'} for d in e1]
            # e23 = [{k: v for k, v in d.items() if k != 'password'} for d in e22]
            # e24 = [{k: v for k, v in d.items() if k != 'city'} for d in e23]
            e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1] #remove the _id key-value from extracted document
            e22 = e2[1:]
            print('e22--------------------------------------------------------------------',e22)
      
            even = len(e22)
            print(even)


            now = datetime.now() 
            remindTime1 = now.strftime("%Y-%m-%d %H:%M")
            remindTime = datetime.strptime(remindTime1,"%Y-%m-%d %H:%M") #current date and time
            eve_time1 = e1[1].get('end')+" "+e1[1].get('endTime') 
            eve_time = datetime.strptime(eve_time1,"%Y-%m-%d %H:%M")
            eveTime_early = eve_time - timedelta(hours=2) #time and date of event with earliest endtime
            print(type(remindTime))
            print(type(eve_time))

            
               # e02 = [{k: v for k, v in d.items() if k != '_id'} for d in e01] #remove the _id key-value from extracted document
            
            # auto-delete events of past date
            today = date.today()
            e03 = [a_dict['end'] for a_dict in e22]
            for i in e03:
               di = datetime.strptime(i, "%Y-%m-%d").date()
               if today>di:
                  db.schedulardb.delete_one({'username':un, 'password':ps, 'end':i})
            

           

            # e1 = list(db.schedulardb.find().sort([("end", 1), ("endTime", 1),("startTime",1)]))   # Sorting the collection from database.
            # print(e1[0].get('title'))
            # # print(type(e1))
            # e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1]

            

            for k in e22:
               now = datetime.now() 
               remindTime1 = now.strftime("%Y-%m-%d %H:%M")
               remindTime = datetime.strptime(remindTime1,"%Y-%m-%d %H:%M") #current date and time
               eve_time1 = k.get('end')+" "+k.get('endTime') 
               eve_time = datetime.strptime(eve_time1,"%Y-%m-%d %H:%M")
               eveTime_early = eve_time - timedelta(hours=2) #time and date of event with earliest endtime
               print("remind",remindTime)
               print("early",eveTime_early)
               
               if(k.get('sentMail')==0):
                  print("inside if 1")
                  if(remindTime>=eveTime_early):
                     # tempEve = e1[0].get('title')
                     print("inside if 2")

                     print(mail)
                     msg = Message(
                                 k.get('title')+' deadline creeping up!',
                                 sender ='schedularxp@gmail.com',
                                 recipients = [un]
                                 )
                     msg.body = 'Deadline for '+k.get('title')+' is due on '+k.get('end')+' at '+k.get('endTimeap')
                     mail.send(msg)

                     # print(e2)
               
                     # print(even)

                     newvalues = { "$set": { "sentMail": 1} }
                     query = { "sentMail": 0 }

                     db.schedulardb.update_one(query, newvalues)
            even = len(e22)
            weatherData = weather(ct)
            print('e22 get-----------------',e22)
           
            return render_template('calendar_page.html',events = e22,n = even, data = [Item(i) for i in e22],weatherData = weatherData)
      #return render_template('calendar_page.html',events = [],n = 0, data = [],weatherData = weatherData)


   weatherData = weather(ct)
   return render_template('calendar_page.html',events = [],n = 0, data = [],weatherData = weatherData)


@app.route('/deleteData', methods=['GET','POST'])
def data_del():
   un = session.get('emailid')
   ps = session.get('ps')
   ct = session.get('ct')
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


         db.schedulardb.delete_one({'username':un, 'password':ps, 'start':startDate,'title': eTitle, 'startTime': startTime, 'endTime':endTime,'end':endDate})
         e1 = list(db.schedulardb.find({'username':un, 'password':ps}).sort([("end", 1), ("endTime", 1),("startTime",1)]))
         # print(e1)
         # print(type(e1))
         e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1]
         e22 = e2[1:]
         even = len(e22)
         print("Event deleted")
   weatherData = weather(ct)
   return render_template('/calendar_page.html',events = e22,n = even, data = [Item(i) for i in e22],weatherData = weatherData)

@app.route('/Logout')
def Logout():
   session['emailid'] = None
   session['ct'] = None
   session['ps'] = None

   return redirect(url_for('index'))


if __name__ == '__main__':
   app.run(debug = True)