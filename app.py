from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'home2'

@app.route('/user/<username>')
def username(username):
    return 'i am ' + username

def index():
    return 'hello man'
    
if __name__ == '__main__':
    app.debug = True
    app.run()