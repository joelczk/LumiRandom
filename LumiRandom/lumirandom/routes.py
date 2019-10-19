import os
from lumirandom import app, db, bcrypt
from lumirandom.forms import RegistrationForm, LoginForm, UpdateAccountForm
from lumirandom.models import User, Students, Courses, TakenCourses, Professors, TeachingAssistants, Groups, GroupInfo, Posts, role_required
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func
import secrets
from PIL import Image
from random import randint
import datetime, sys

cur_year = '2019/2020'
cur_sem = 1


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
        user = User(name=form.f_name.data + ' ' + form.l_name.data, id=form.account_id.data, password=hashed_password)
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
        user = User.query.filter_by(id=form.account_id.data).first()
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
    User.query.get_or_404(id)
    user = User.query.get(id)
    roles = user.roles()
    student = Students()
    prof = Professors()
    return render_template('profile.html', title='Profile ' + id, user=user, roles=roles, student=student, prof=prof)


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
        return redirect(url_for('profile', id=current_user.id))
    return render_template('update_profile.html', title='Update Profile', student=student, prof=prof, form=form)


@app.route("/mymodules")
@login_required
@role_required(role='Student')
def modules():
    takingmods = TakenCourses.query.filter(TakenCourses.sid==current_user.id, TakenCourses.year==cur_year, TakenCourses.sem==cur_sem)
    takenmods = TakenCourses.query.filter(TakenCourses.sid==current_user.id, TakenCourses.year!=cur_year or (TakenCourses.year==cur_year and TakenCourses.sem<cur_sem)).order_by(TakenCourses.year.desc(), TakenCourses.sem.desc())
    mods = Courses()
    profs = Professors()
    return render_template('mymodules.html', title='My Modules', takingmods=takingmods, takenmods=takenmods, mods=mods, profs=profs, cur_year=cur_year, cur_sem=cur_sem)


@app.route("/module-search", methods=['GET', 'POST'])
@app.route("/module-search/search/<string:query>", methods=['GET', 'POST'])
@login_required
def module_search(query=None):
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
        return render_template('module_search.html', title='Module Search', courses=courses, taken=TakenCourses(), prof=prof, query=query, cur_year=cur_year, cur_sem=cur_sem)
    page = request.args.get('page', 1, type=int)
    courses = Courses.query.order_by(Courses.cid.asc()).paginate(page=page, per_page=15)
    return render_template('module_search.html', title='Module Search', courses=courses, taken=TakenCourses(), prof=prof, query=query, cur_year=cur_year, cur_sem=cur_sem)


@app.route("/module/<string:cid>", methods=['GET', 'POST'])
@login_required
def module(cid):
    Courses.query.get_or_404(cid)
    module = Courses.query.filter_by(cid=cid).first()
    if TakenCourses.query.filter_by(sid=current_user.id, cid=cid).filter(TakenCourses.year!=cur_year or (TakenCourses.year==cur_year and TakenCourses.sem<cur_sem)).first():
        status = "taken"
    elif TakenCourses.query.filter_by(sid=current_user.id, year=cur_year, sem=cur_sem, cid=cid).first():
        status = "taking"
    elif Professors.query.filter_by(cid=cid).first() == None:
        status = "unavailable"
    else:
        status = "nil"
    return render_template('module.html', title=cid, module=module, status=status, cur_year=cur_year, cur_sem=cur_sem)


@app.route("/module/<string:cid>/enrol", methods=['GET', 'POST'])
@login_required
def module_enrol(cid):
    Courses.query.get_or_404(cid)
    if TakenCourses.query.filter_by(sid=current_user.id, cid=cid).filter(TakenCourses.year!=cur_year or (TakenCourses.year==cur_year and TakenCourses.sem<cur_sem)).first():
        flash(f'You have already taken {cid} {Courses.query.get(cid).cname} before.', 'warning')
    elif Professors.query.filter_by(cid=cid).first() == None:
        flash(f'Sorry! {cid} {Courses.query.get(cid).cname} is not available this semester!', 'warning')
    elif TakenCourses.query.filter_by(sid=current_user.id, year=cur_year, sem=cur_sem, cid=cid).first():
        flash(f'You are already enrolled to {cid} {Courses.query.get(cid).cname}!', 'warning')
    else:
        if TakenCourses.query.filter_by(sid=current_user.id, year=cur_year, sem=cur_sem).count() >= 6:
            flash(f'Sorry! You have already enrolled to the maximum number of modules for this semester!', 'warning')
        else:
            course = TakenCourses(sid=current_user.id, cid=cid, year=cur_year, sem=cur_sem)
            db.session.add(course)
            db.session.commit()
            flash(f'You have enrolled to {cid} {Courses.query.get(cid).cname}!', 'success')  
    return redirect(url_for('module', cid=cid))


@app.route("/module/<string:cid>/withdraw", methods=['GET', 'POST'])
@login_required
def module_withdraw(cid):
    Courses.query.get_or_404(cid)
    course = TakenCourses.query.filter_by(sid=current_user.id, year=cur_year, sem=cur_sem, cid=cid).first()
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
    requested = TeachingAssistants.query.filter_by(sid=current_user.id, is_ta=False).all()
    if Students.query.filter(Students.sid==current_user.id, Students.year>1).first():
        takenmods = TakenCourses.query.join(Professors, TakenCourses.cid==Professors.cid).filter(TakenCourses.sid==current_user.id, TakenCourses.year!=cur_year, TakenCourses.grade.like("A%"))
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
    ta = TeachingAssistants.query.filter_by(sid=current_user.id, is_ta=True).first()
    return render_template('ta_signup.html', title='TA Sign Up', available=available, profs=profs, requested=requested, ta=ta)


@app.route("/ta/join/<string:cid>", methods=['GET', 'POST'])
@login_required
@role_required(role='Student')
def ta_join(cid):
    Courses.query.get_or_404(cid)
    if Professors.query.filter_by(cid=cid).first() == None:
        flash(f'Sorry! {cid} {Courses.query.get(cid).cname} is not available this semester!', 'warning')
    elif TeachingAssistants.query.filter_by(sid=current_user.id, is_ta=True).first():
        ta = TeachingAssistants.query.filter_by(sid=current_user.id, is_ta=True).first()
        if ta.cid == cid:
            flash(f'You are already a Teaching Assistant for {ta.cid} {Courses.query.get(ta.cid).cname}!', 'warning')
        else:
            flash(f'You are already a Teaching Assistant for {ta.cid} {Courses.query.get(ta.cid).cname}! You are not allowed to apply to be a Teaching Assistant for any other modules.', 'warning')
    elif TeachingAssistants.query.filter_by(sid=current_user.id, cid=cid).first():
        flash(f'You have already requested to be a Teaching Assistant for {cid} {Courses.query.get(cid).cname}.', 'warning')
    elif TakenCourses.query.get([current_user.id, cid]).grade[0] != 'A' or Students.query.get(current_user.id).year == 1:
        flash(f'Sorry! You are not eligible to be a Teaching Assistant for {cid} {Courses.query.get(cid).cname}!', 'warning')
    else:
        ta = TeachingAssistants(sid=current_user.id, cid=cid, is_ta=False)
        db.session.add(ta)
        db.session.commit()
        flash(f'Thank you for requesting to be a Teaching Assistant for {cid} {Courses.query.get(cid).cname}! Awaiting confirmation from Professor.', 'success')  
    return redirect(url_for('ta_signup'))


@app.route("/ta/withdraw/<string:cid>", methods=['GET', 'POST'])
@login_required
@role_required(role='Student')
def ta_withdraw(cid):
    Courses.query.get_or_404(cid)
    if TeachingAssistants.query.filter_by(sid=current_user.id, cid=cid, is_ta=True).first():
        flash(f'You are already a Teaching Assistant for {cid} {Courses.query.get(cid).cname} and are not allowed to withdraw anymore.', 'danger')
        return redirect(url_for('ta_signup'))
    mod = TeachingAssistants.query.filter_by(sid=current_user.id, cid=cid).first()
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
    tas = TeachingAssistants.query.filter_by(cid=cid, is_ta=True).all()
    requests = TeachingAssistants.query.filter_by(cid=cid, is_ta=False).all()
    students = Students()
    user = User()
    return render_template('my_tas.html', title='My TAs', cid=cid, tas=tas, requests=requests, students=students, user=user, cur_year=cur_year, cur_sem=cur_sem)


@app.route("/prof/accept/<string:sid>", methods=['GET', 'POST'])
@login_required
@role_required(role='Professor')
def ta_accept(sid):
    Students.query.get_or_404(sid)
    if TeachingAssistants.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid).first() == None:
        flash(f'Invalid Request!', 'danger')
    else:
        othersignups = TeachingAssistants.query.filter_by(sid=sid).all()
        for othersignup in othersignups:
            db.session.delete(othersignup)
        ta = TeachingAssistants(sid=sid, cid=Professors.query.get(current_user.id).cid, is_ta=True)
        db.session.add(ta)
        db.session.commit()
        flash(f'Success! {Students.query.get(sid).info.name} is now your slave!', 'success')  
    return redirect(url_for('my_tas'))


@app.route("/prof/reject/<string:sid>", methods=['GET', 'POST'])
@login_required
@role_required(role='Professor')
def ta_reject(sid):
    Students.query.get_or_404(sid)
    if TeachingAssistants.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid).first() == None:
        flash(f'Invalid Request!', 'danger')
    elif TeachingAssistants.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid, is_ta=True).first():
        student = TeachingAssistants.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid, is_ta=True).first()
        db.session.delete(student)
        db.session.commit()
        flash(f'{Students.query.get(sid).info.name} is no longer your slave!', 'warning')  
    else:
        student = TeachingAssistants.query.filter_by(sid=sid, cid=Professors.query.get(current_user.id).cid).first()
        db.session.delete(student)
        db.session.commit()
        flash(f'{Students.query.get(sid).info.name} is rejected from being your slave!', 'warning')  
    return redirect(url_for('my_tas'))


@app.route("/mygroups")
@login_required
@role_required(role='Student')
def my_groups():
    groups = GroupInfo.query.filter_by(sid=current_user.id).all()
    user = User()
    return render_template('my_groups.html', title='Groups', groups=groups, groupinfo=GroupInfo(), user=user)

@app.route("/group/<int:gid>")
@login_required
def group(gid):
    is_student = is_ta = is_prof = False
    if Students.query.get(current_user.id):
        is_student = True
    if TeachingAssistants.query.filter_by(sid=current_user.id, is_ta=True).first():
        is_ta = True
    if Professors.query.get(current_user.id):
        is_prof = True
    if (is_student and GroupInfo.query.filter(GroupInfo.gid==gid, GroupInfo.sid==current_user.id).first()) or (is_ta and current_user.id==Groups.query.get(gid).sid) \
        or (is_prof and current_user.id==Groups.query.get(gid).pid):
        group = Groups.query.get(gid)
        students = GroupInfo.query.join(User, GroupInfo.sid==User.id).filter(GroupInfo.gid==gid).order_by(User.name.asc()).all()
        size = GroupInfo.query.filter_by(gid=group.gid).count()
        return render_template('group.html', title='Group', group=group, students=students, size=size, user=User())
    else:
        abort(403)


@app.route("/prof/groups")
@login_required
@role_required(role='Professor')
def prof_groups():
    groups = Groups.query.filter_by(pid=current_user.id).all()
    groupinfo = GroupInfo()
    cid = Professors.query.get(current_user.id).cid
    user = User()
    return render_template('prof_groups.html', title='Groups', groups=groups, groupinfo=groupinfo, user=user, cid=cid)


@app.route("/prof/create-group", methods=['GET', 'POST'])
@login_required
@role_required(role='Professor')
def create_group():
    if request.method == 'POST':
        gname = request.form['gname']
        students = request.form['students'].split(',')
        ta = request.form['ta']
        if ta == "none":
            ta = ''
        if Groups.query.first() == None:
            gid = 1
        else:
            gid = db.session.query(func.max(Groups.gid)).scalar()+1
        g = Groups(gid=gid, gname=gname, pid=current_user.id, sid=ta)
        db.session.add(g)
        for student in students:
            s = GroupInfo(gid=gid, sid=student)
            db.session.add(s)
        db.session.commit()
        flash(f'New group {gname} successfully created!', 'success')
        return redirect(url_for('prof_groups'))

    cid = Professors.query.get(current_user.id).cid
    students = TakenCourses.query.join(User, TakenCourses.sid==User.id).filter(TakenCourses.cid==cid, TakenCourses.year==cur_year, TakenCourses.sem==cur_sem).order_by(User.name.asc()).all()
    s1, s2, s3, s4, s5 = ([] for i in range(5))
    for student in students:
        if student.student.year == 1:
            s1.append(student)
        elif student.student.year == 2:
            s2.append(student)
        elif student.student.year == 3:
            s3.append(student)
        elif student.student.year == 4:
            s4.append(student)
        elif student.student.year == 5:
            s5.append(student)
    tas = TeachingAssistants.query.join(User, TeachingAssistants.sid==User.id).filter(TeachingAssistants.cid==cid).order_by(User.name.asc()).all()   
    return render_template('create_group.html', title='Create Group', students=students, s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, tas=tas, cid=cid)



@app.route("/module/<string:cid>/forums/create_post", methods=['GET', 'POST'])
@login_required
def createpost(cid):
    Courses.query.get_or_404(cid)
    module = Courses.query.get(cid)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['contents']
        randnumber = randint(0,sys.maxsize)
        post_num = randint(0,2**31) % randnumber
        datetime_obj = datetime.datetime.now()
        #FID is set to 1 temporarily first until fid has been created 
        fid = 1
        rating = None
        if title == '' or content == '':
            flash(f'Invalid Fields!', 'danger')
        # elif Courses.query.filter_by(cid = mods).first() == None:
        #     flash(f'Invalid Module Code!', 'danger')
        elif Posts.query.filter_by(title = title).first() != None:
            flash(f'Title already exists', 'danger')
        else:
            # print("mods:",mods)
            # print("title:", title)
            # print("contents:", content)
            # print("fid:",fid)
            # print("datetime:", datetime_obj)
            # print(current_user.id)
            if Students.query.get(current_user.id):
                post = Posts(post_num = post_num, fid = fid, pid = None, sid=current_user.id, title = title, content = content, date_posted = datetime_obj, rating = rating)
                db.session.add(post)
                db.session.commit()
            elif Professors.query.get(current_user.id):
                post = Posts(post_num = post_num, fid = fid, pid=current_user.id, sid = None, title = title, content = content, date_posted = datetime_obj, rating = rating)
                db.session.add(post)
                db.session.commit()
            flash(f'Post created successfully.', 'success')
            return render_template('create_post.html', title = "Create Post", module = module)
    return render_template('create_post.html',title = "Create Post", module = module)


@app.errorhandler(404)
def Error404(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def Error403(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def Error500(error):
    return render_template('errors/500.html'), 500