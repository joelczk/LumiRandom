import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from lumirandom import app, db, bcrypt
from lumirandom.forms import RegistrationForm, LoginForm, UpdateAccountForm
from lumirandom.models import User, Students, Courses, TakenCourses, TakingCourses, Professors, PossibleTA, TeachingAssistants, role_required
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
        user = User(name=form.f_name.data + ' ' + form.l_name.data, account_id=form.account_id.data, password=hashed_password)
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
        user = User.query.filter_by(account_id=form.account_id.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome {user.name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid ID or Password. Please try again.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash(f'Logout Successful! Please Visit Again!', 'success')
    return redirect(url_for('home'))


@app.route("/profile/<string:id>")
@login_required
def profile(id):
    User.query.get_or_404(User.query.filter_by(account_id=id).first().id)
    user = User.query.filter_by(account_id=id).first()
    roles = user.roles
    student = Students()
    prof = Professors()
    return render_template('profile.html', title='Profile', user=user, roles=roles, student=student, prof=prof)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_fn)

    old_picture = current_user.image_file
    if old_picture != 'default.jpg':
        delete_picture_path = os.path.join(app.root_path, 'static/profile_pictures', old_picture)
        os.remove(delete_picture_path)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/update-profile", methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateAccountForm()
    student = Students()
    prof = Professors()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if form.confirm_password.data:
            hashed_password = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf-8')
            current_user.password = hashed_password
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile', id=current_user.account_id))
    return render_template('update_profile.html', title='Update Profile', student=student, prof=prof, form=form)


@app.route("/mymodules")
@login_required
@role_required(role='Student')
def modules():
    takingmods = TakingCourses.query.filter_by(sid=current_user.id)
    takenmods = TakenCourses.query.filter_by(sid=current_user.id).order_by(TakenCourses.year.desc(), TakenCourses.sem.desc())
    mods = Courses()
    profs = Professors()
    return render_template('mymodules.html', title='My Modules', takingmods=takingmods, takenmods=takenmods, mods=mods, profs=profs)


@app.route("/module-search", methods=['GET', 'POST'])
@app.route("/module-search/search/<string:query>", methods=['GET', 'POST'])
@login_required
def module_search(query=None):
    taken = TakenCourses()
    taking = TakingCourses()
    prof = Professors()
    if request.method == "POST":
        cid = request.form['search']
        if len(cid) <= 1:
            flash(f'Please enter more than 1 character!','warning')
        else:
            return redirect(url_for('module_search', query=cid))
    if query:
        querystr = '%' + query + '%'
        page = request.args.get('page', 1, type=int)
        courses = Courses.query.filter(Courses.cid.like(querystr)).order_by(Courses.cid.asc()).paginate(page=page, per_page=15)
        return render_template('module_search.html', title='Module Search', courses=courses, taken=taken, taking=taking, prof=prof, query=query)
    page = request.args.get('page', 1, type=int)
    courses = Courses.query.order_by(Courses.cid.asc()).paginate(page=page, per_page=15)
    return render_template('module_search.html', title='Module Search', courses=courses, taken=taken, taking=taking, prof=prof, query=query)


@app.route("/module/<string:cid>", methods=['GET', 'POST'])
@login_required
def module(cid):
    Courses.query.get_or_404(cid)
    module = Courses.query.filter_by(cid=cid).first()
    if TakenCourses.query.filter_by(sid=current_user.id, cid=cid).first():
        status = "taken"
    elif TakingCourses.query.filter_by(sid=current_user.id, cid=cid).first():
        status = "taking"
    elif Professors.query.filter_by(cid=cid).first() == None:
        status = "unavailable"
    else:
        status = "nil"
    return render_template('module.html', title=cid, module=module, status=status)


@app.route("/module/<string:cid>/enrol", methods=['GET', 'POST'])
@login_required
def module_enrol(cid):
    Courses.query.get_or_404(cid)
    if TakenCourses.query.filter_by(sid=current_user.id, cid=cid).first():
        flash(f'You have already taken {cid} {Courses.query.get(cid).cname} before.', 'warning')
    elif Professors.query.filter_by(cid=cid).first() == None:
        flash(f'Sorry! {cid} {Courses.query.get(cid).cname} is not available this semester!', 'warning')
    elif TakingCourses.query.filter_by(sid=current_user.id, cid=cid).first():
        flash(f'You are already enrolled to {cid} {Courses.query.get(cid).cname}!', 'warning')
    else:
        if TakingCourses.query.filter_by(sid=current_user.id).count() >= 6:
            flash(f'Sorry! You have already enrolled to the maximum number of modules for this semester!', 'warning')
        else:
            course = TakingCourses(sid=current_user.id, cid=cid)
            db.session.add(course)
            db.session.commit()
            flash(f'You have enrolled to {cid} {Courses.query.get(cid).cname}!', 'success')  
    return redirect(url_for('module', cid=cid))


@app.route("/module/<string:cid>/withdraw", methods=['GET', 'POST'])
@login_required
def module_withdraw(cid):
    Courses.query.get_or_404(cid)
    course = TakingCourses.query.filter_by(sid=current_user.id, cid=cid).first()
    if course:
        db.session.delete(course)
        db.session.commit()
        flash(f'You have withdrawn from {cid}!', 'warning')
    else:
        flash(f'You are not enrolled to {cid}!', 'danger')
    return redirect(url_for('module', cid=cid))


@app.route("/student_list/", methods=['GET', 'POST'])
@app.route("/student_list/search/<string:query>", methods=['GET', 'POST'])
@login_required
def student_list(query=None):
    if request.method == "POST":
        s_name = request.form['search']
        if len(s_name) <= 1:
            flash(f'Please enter more than 1 character!','warning')
        else:
            return redirect(url_for('student_list', query=s_name))
    if query:
        querystr = '%' + query + '%'
        page = request.args.get('page', 1, type=int)
        students = Students.query.join(User, Students.sid==User.id).filter(User.name.like(querystr)).order_by(Students.year.asc(), User.name.asc()).paginate(page=page, per_page=15)
        return render_template('student_list.html', title='Student List', students=students, query=query)
    page = request.args.get('page', 1, type=int)
    students = Students.query.join(User, Students.sid==User.id).order_by(Students.year.asc(), User.name.asc()).paginate(page=page, per_page=15)
    return render_template('student_list.html', title='Student List', students=students, query=query)


@app.route("/tutors")
@login_required
def staff():
    return render_template("staff.html", title='Tutors')


@app.route("/ta/signup", methods=['GET', 'POST'])
@login_required
@role_required(role='Student')
def ta_signup():
    requested = PossibleTA.query.filter_by(sid=current_user.id).all()
    if Students.query.filter(Students.sid==current_user.id, Students.year>1).first():
        takenmods = TakenCourses.query.join(Professors, TakenCourses.cid==Professors.cid).filter(TakenCourses.sid==current_user.id, TakenCourses.grade.like("A%"))
        available = []
        for takenmod in takenmods:
            found = False
            for request in requested:
                if takenmod.cid == request.cid:
                    found = True
                    break
            if not found:
                available.append(takenmod)
    else:
        available = None
    profs = Professors()
    tas = TeachingAssistants()
    return render_template('ta_signup.html', title='TA Sign Up', available=available, profs=profs, requested=requested, tas=tas)


@app.route("/ta/join/<string:cid>", methods=['GET', 'POST'])
@login_required
@role_required(role='Student')
def ta_join(cid):
    Courses.query.get_or_404(cid)
    if TeachingAssistants.query.filter_by(sid=current_user.id).first():
        ta = TeachingAssistants.query.get(current_user.id)
        if ta.cid == cid:
            flash(f'You are already a Teaching Assistant for {ta.cid} {Courses.query.get(ta.cid).cname}!', 'warning')
        else:
            flash(f'You are already a Teaching Assistant for {ta.cid} {Courses.query.get(ta.cid).cname}! You are not allowed to apply to be a Teaching Assistant for any other modules.', 'warning')
        return redirect(url_for('ta_signup'))
    if PossibleTA.query.filter_by(sid=current_user.id, cid=cid).first():
        flash(f'You have already requested to be a Teaching Assistant for {cid} {Courses.query.get(cid).cname}.', 'warning')
    elif Professors.query.filter_by(cid=cid).first() == None:
        flash(f'Sorry! {cid} {Courses.query.get(cid).cname} is not available this semester!', 'warning')
    elif TakenCourses.query.get([current_user.id, cid]).grade[0] != 'A' or Students.query.get(current_user.id).year == 1:
        flash(f'Sorry! You are not eligible to be a Teaching Assistant for {cid} {Courses.query.get(cid).cname}!', 'warning')
    else:
        ta = PossibleTA(sid=current_user.id, cid=cid)
        db.session.add(ta)
        db.session.commit()
        flash(f'Thank you for requesting to be a Teaching Assistant for {cid} {Courses.query.get(cid).cname}! Awaiting confirmation from Professor.', 'success')  
    return redirect(url_for('ta_signup'))


@app.route("/ta/withdraw/<string:cid>", methods=['GET', 'POST'])
@login_required
@role_required(role='Student')
def ta_withdraw(cid):
    Courses.query.get_or_404(cid)
    if TeachingAssistants.query.filter_by(sid=current_user.id, cid=cid).first():
        flash(f'You are already a Teaching Assistant for {cid} {Courses.query.get(cid).cname} and are not allowed to withdraw anymore.', 'danger')
        return redirect(url_for('ta_signup'))
    mod = PossibleTA.query.filter_by(sid=current_user.id, cid=cid).first()
    if mod:
        db.session.delete(mod)
        db.session.commit()
        flash(f'You have withdrawn your application as a Teaching Assistant for {cid} {Courses.query.get(cid).cname}.', 'warning')
    else:
        flash(f'You have not signed up to be a Teaching Assistant for {mod} {Courses.query.get(cid).cname}.', 'info')
    return redirect(url_for('ta_signup'))
  


@app.route("/prof_list", methods=['GET', 'POST'])
@app.route("/prof_list/search/<string:query>", methods=['GET', 'POST'])
@login_required
def prof_list(query=None):
    if request.method == "POST":
        p_name = request.form['search']
        if len(p_name) <= 1:
            flash(f'Please enter more than 1 character!','warning')
        else:
            return redirect(url_for('prof_list', query=p_name))
    if query:
        querystr = '%' + query + '%'
        page = request.args.get('page', 1, type=int)
        profs = Professors.query.join(User, Professors.pid==User.id).filter(User.name.like(querystr)).order_by(User.name.asc()).paginate(page=page, per_page=15)
        return render_template('prof_list.html', title='Professor List', profs=profs, query=query)
    page = request.args.get('page', 1, type=int)
    profs = Professors.query.join(User, Professors.pid==User.id).order_by(User.name.asc()).paginate(page=page, per_page=15)
    return render_template('prof_list.html', title='Professor List', profs=profs, query=query)


@app.route("/prof/mytas")
@login_required
@role_required(role='Professor')
def my_tas():
    cid = Professors.query.get(current_user.id).cid
    tas = TeachingAssistants()
    requests = PossibleTA.query.filter_by(cid=cid).all()
    students = Students()
    user = User()
    return render_template('my_tas.html', title='My TAs', cid=cid, tas=tas, requests=requests, students=students, user=user)


@app.route("/prof/accept/<string:sid>", methods=['GET', 'POST'])
@login_required
@role_required(role='Professor')
def ta_accept(sid):
    Students.query.get_or_404(sid)
    if PossibleTA.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid).first() == None:
        flash(f'Invalid Request!', 'danger')
    else:
        othersignups = PossibleTA.query.filter_by(sid=sid).all()
        for othersignup in othersignups:
            db.session.delete(othersignup)
        ta = TeachingAssistants(sid=sid, cid=Professors.query.get(current_user.id).cid)
        ta2 = PossibleTA(sid=sid, cid=Professors.query.get(current_user.id).cid)
        db.session.add(ta)
        db.session.add(ta2)
        db.session.commit()
        flash(f'Success! {Students.query.get(sid).info.name} is now your slave!', 'success')  
    return redirect(url_for('my_tas'))


@app.route("/prof/reject/<string:sid>", methods=['GET', 'POST'])
@login_required
@role_required(role='Professor')
def ta_reject(sid):
    Students.query.get_or_404(sid)
    if PossibleTA.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid).first() == None:
        flash(f'Invalid Request!', 'danger')
    elif TeachingAssistants.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid).first():
        student = TeachingAssistants.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid).first()
        db.session.delete(student)
        db.session.commit()
        flash(f'{Students.query.get(sid).info.name} is no longer your slave!', 'warning')  
    else:
        student = PossibleTA.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid).first()
        db.session.delete(student)
        db.session.commit()
        flash(f'{Students.query.get(sid).info.name} is rejected from being your slave!', 'warning')  
    return redirect(url_for('my_tas'))