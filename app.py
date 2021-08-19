from flask import Flask, render_template,request,jsonify,json
from flask_pymongo import PyMongo
from pymongo import message

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
         eventDate = '2021-07-14'
         eventName = requestInput.get('name')
         eventDes = requestInput.get('content1')
         eventType = requestInput.get('optradio')
         eventSt = requestInput.get('stTime')
         eventEnd = requestInput.get('endTime')
         if(len(eventName)>0):
            db.schedulardb.insert_one({'Start':eventDate, 'title':eventName })
            print("insert running")
            
            e1 = list(db.schedulardb.find())
            print(e1)
            print(type(e1))
            e2 = [{k: v for k, v in d.items() if k != '_id'} for d in e1] #remove the _id key-value from extracted document
            print(e2)
            even = len(e2)
            print(even)


   return render_template('/calendar_page.html',events = e2,n = even, data = [Item(i) for i in e2])



# @app.route('/getdata/<dt>', methods=['GET','POST'])
# def data_get(dt):
    


if __name__ == '__main__':
   app.run(debug = True)