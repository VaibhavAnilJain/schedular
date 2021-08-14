from flask import Flask, render_template,request

app = Flask(__name__)

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/calendarPage',methods=["GET","POST"])
def calendar_page():
   if request.method== "POST":
         x=request.form
         y=x['date']
         print(y)
         Message={"Message":"problem solved"}
         return Message

   a = 'hello'
   return render_template('calendar_page.html', a = a)

# @app.route('/getdata/<dt>', methods=['GET','POST'])
# def data_get(dt):
    


if __name__ == '__main__':
   app.run(debug = True)