from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/calendarPage')
def calendar_page():
   return render_template('calendar_page.html')

# @app.route('/getdata/<dt>', methods=['GET','POST'])
# def data_get(dt):
    


if __name__ == '__main__':
   app.run(debug = True)