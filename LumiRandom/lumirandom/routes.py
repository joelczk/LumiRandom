from flask import render_template, url_for, flash, redirect, request, abort
from lumirandom import app, db, bcrypt
from lumirandom.forms import RegistrationForm, LoginForm
from lumirandom.models import User, Post, Students, SAccount, Courses, TakenCourses, TakingCourses, Professors, PAccount
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = SAccount(name=form.f_name.data + ' ' + form.l_name.data, account_id=form.account_id.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.f_name.data} {form.l_name.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = SAccount.query.filter_by(account_id=form.account_id.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome {user.name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please try again.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash(f'Logout Successful! Please Visit Again!', 'success')
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/mymodules")
@login_required
def modules():
    takingmods = TakingCourses.query.filter_by(sid=current_user.sid)
    takenmods = TakenCourses.query.filter_by(sid=current_user.sid).order_by(TakenCourses.year.desc(), TakenCourses.sem.desc())
    mods = Courses()
    profs = Professors()
    return render_template('mymodules.html', title='My Modules', takingmods=takingmods, takenmods=takenmods, mods=mods, profs=profs)


@app.route("/module-search", methods=['GET', 'POST'])
@login_required
def module_search():
    if request.method == "POST":
        id = request.form['search']
        cse_id = Courses.query.filter_by(cid = id).first()
        return render_template('module_search.html', title = 'Module Search', courses_show = cse_id)
    page = request.args.get('page', 1, type=int)
    courses = Courses.query.order_by(Courses.cid.asc()).paginate(page=page, per_page=15)
    return render_template('module_search.html', title='Module Search', courses=courses)



@app.route("/module/<string:cid>", methods=['GET', 'POST'])
@login_required
def module(cid):
    module = Courses.query.filter_by(cid=cid).first()
    if TakenCourses.query.filter_by(sid=current_user.sid, cid=cid).first():
        status = "taken"
    elif TakingCourses.query.filter_by(sid=current_user.sid, cid=cid).first():
        status = "taking"
    else:
        status = "nil"
    return render_template('module.html', title=cid, module=module, status=status)


@app.route("/module/<string:cid>/enrol", methods=['GET', 'POST'])
@login_required
def module_enrol(cid):
    if TakenCourses.query.filter_by(sid=current_user.sid, cid=cid).first():
        flash(f'You have already taken {cid} before.', 'warning')
    elif Professors.query.filter_by(cid=cid).first() == None:
        flash(f'Sorry! {cid} is not available this semester!', 'warning')
    elif TakingCourses.query.filter_by(sid=current_user.sid, cid=cid).first():
        flash(f'You already enrolled to {cid}!', 'warning')
    else:
        if TakingCourses.query.filter_by(sid=current_user.sid).count() >= 6:
            flash(f'Sorry! You have already enrolled to the maximum number of modules for this semester!', 'warning')
        else:
            course = TakingCourses(sid=current_user.sid, cid=cid)
            db.session.add(course)
            db.session.commit()
            flash(f'You have enrolled to {cid}!', 'success')  
    return redirect(url_for('module', cid=cid))


@app.route("/module/<string:cid>/withdraw", methods=['GET', 'POST'])
@login_required
def module_withdraw(cid):
    course = TakingCourses.query.filter_by(sid=current_user.sid, cid=cid).first()
    if course:
        db.session.delete(course)
        db.session.commit()
        flash(f'You have withdrawn from {cid}!', 'warning')
    else:
        flash(f'You are not enrolled to {cid}!', 'danger')
    return redirect(url_for('module', cid=cid))


@app.route("/students", methods=['GET', 'POST'])
@login_required
def students():
    if request.method == "POST":
        name = request.form['search']
        student = Students.query.filter_by(name = name).first()
        return render_template('student.html', title = 'Student List', students_search = student)
    page = request.args.get('page', 1, type=int)
    students = Students.query.order_by(Students.year.asc(), Students.name.asc()).paginate(page=page, per_page=15)
    return render_template('student.html', title='Student List', students=students)

@app.route("/tutors")
@login_required
def staff():
    return render_template("staff.html", title='Staff')
