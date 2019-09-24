from flask import Flask, render_template

app = Flask(__name__)

@app.route("/index.html")
def index():
    return render_template('index.html')

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login.html")
def login():
    return render_template('login.html')

@app.route("/register.html")
def register():
    return render_template('register.html')

@app.route("/tutor_login.html")
def tutor_login():
    return render_template('tutor_login.html')
    
@app.route("/student_login.html")
def student_login():
    return render_template('student_login.html')

  
if __name__ == "__main__":
    app.run(debug = True, host = 'localhost', port = 5000)
