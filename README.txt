Dependencies:
pip install flask
pip install Flask-SQLAlchemy
pip install Flask-Bcrypt
pip install Flask-Login
pip install Flask-User
pip install Pillow
pip install psycopg2

Setting up database:
1. Create tables by copying the tables in sql.txt into your personal psql
2. Populate each table with the queries inside POSTGRES SQL/<table name>.txt
3. Populate each table according to the first number of the file number(i.e.Users->Students->Courses->TakenCourses->TeachingAssistants->
   Professors->Groups->GroupInfo->Forums->ForumInfo)
4. Go to __init.py__ and change the following lines of code:
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{username}:{password}@{host}:{port}/{database}'\
    .format(
        username='<your username>',
        password='<your password>',      # Change accordingly
        host='<your host>',
        port=<your port number>,
        database='<your database>'   # Change accordingly
    )
   connection = psycopg2.connect(user="<your username>", password="<your password>", host="<your host>", port="<your port number>", database="<your database>")

Setup:
1.Download the file directory into your preferred file location
2.From command prompt/anaconda prompt cd <file location>/<file name>/LumiRandom.Afterwards run command 'py start.py'
3.Afterwards, enter command 'localhost:5300' in your preferred browser
4. To log into a student account, choose any username from S00001 to S01000
5. To log into a professor account, choose any username from P00001 to P00100
6. The password for both student and professor accounts are 'password'

Languages used: python, JavaScript, HTML, CSS

The project repository is also available at https://github.com/joelczk/CS2102-Project

