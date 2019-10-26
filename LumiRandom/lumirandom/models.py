from datetime import datetime
from lumirandom import db, login_manager
from flask import abort
from flask_login import UserMixin, current_user
from functools import wraps


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def role_required(role='all'):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if role == 'all':
                return fn(*args, **kwargs)
            if role == 'Student' and Students.query.get(current_user.id):
                return fn(*args, **kwargs)
            elif role == 'TA' and TeachingAssistants.query.filter_by(sid=current_user.id, is_ta='t').first():
                return fn(*args, **kwargs)
            elif role == 'Professor' and Professors.query.get(current_user.id):
                return fn(*args, **kwargs)
            return abort(403)
        return decorated_view
    return wrapper


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(100), nullable=False, server_default='default.jpg')
    password = db.Column(db.String(20), nullable=False)
    student = db.relationship('Students', backref='info', lazy=True)
    prof = db.relationship('Professors', backref='info', lazy=True)
    thread = db.relationship('Threads', backref='creator', lazy=True)
    post = db.relationship('Posts', backref='author', lazy=True)

    def roles(self):
        role = []
        if Students.query.get(self.id):
            role.append("Student")
        if TeachingAssistants.query.filter_by(sid=self.id, is_ta='t').first():
            role.append("TA")
        if Professors.query.get(self.id):
            role.append("Professor")
        return role

    def get_id(self):
        return (self.id)

    def __repr__(self):
        return f"User('{self.id}',  {self.name}', '{self.image_file}')"


# class Roles(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(50), unique=True)
#     user_role = db.relationship('UserRoles', backref='role', lazy=True)

#     def __repr__(self):
#         return f"Roles('{self.name}')"


# class UserRoles(db.Model):
#     __tablename__ = 'userroles'
#     id = db.Column(db.Integer(), primary_key=True)
#     user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
#     role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)

#     def __repr__(self):
#         return f"UserRoles('{self.user_id}', '{self.role.name}')"


class Students(db.Model):
    __tablename__ = "students"
    sid = db.Column(db.String(10), db.ForeignKey('users.id'), primary_key=True)
    year = db.Column(db.Integer, db.CheckConstraint('year >= 1 AND year <= 5'), nullable=False)
    taken = db.relationship('TakenCourses', backref='student', lazy=True)
    ta = db.relationship('Groups', backref='ta', lazy=True)
    group = db.relationship('GroupInfo', backref='student', lazy=True)

    def __repr__(self):
        return f"Students('{self.sid}', '{self.year}')"


# class SAccount(db.Model, UserMixin):
#     __tablename__ = "saccount"
#     __table_args__ = (
#         db.ForeignKeyConstraint(['sid', 'name'], ['students.sid', 'students.name']),
#     )
#     sid = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     account_id = db.Column(db.String(10), unique=True, nullable=False)
#     password = db.Column(db.String(60), nullable=False)
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

#     def get_id(self):
#         return (self.sid)

#     def __repr__(self):
#         return f"SAccount('{self.sid}', '{self.name}', '{self.account_id}', '{self.image_file}'"


class Courses(db.Model):
    __tablename__ = "courses"
    cid = db.Column(db.String(10), primary_key=True)
    cname = db.Column(db.String(100), nullable=False)
    taken = db.relationship('TakenCourses', backref='courseinfo', lazy=True)
    prof = db.relationship('Professors', backref='courseinfo', lazy=True)

    def __repr__(self):
        return f"Courses('{self.cid}', '{self.cname}')"


class TakenCourses(db.Model):
    __tablename__ = "takencourses"
    sid = db.Column(db.String(10), db.ForeignKey('students.sid'), primary_key=True)
    cid = db.Column(db.String(10), db.ForeignKey('courses.cid'), primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    sem = db.Column(db.Integer, db.CheckConstraint('sem = 1 OR sem = 2'), nullable=False)
    grade = db.Column(db.String(5), server_default='')
    ta = db.relationship('TeachingAssistants', backref='courseinfo', lazy=True)

    def __repr__(self):
        return f"TakenCourses('{self.sid}', '{self.cid}', '{self.year}', '{self.sem}', '{self.grade}')"


# class TakingCourses(db.Model):
#     __tablename__ = "takingcourses"
#     sid = db.Column(db.Integer, db.ForeignKey('students.sid'), primary_key=True)
#     cid = db.Column(db.String(10), db.ForeignKey('courses.cid'), primary_key=True)

#     def __repr__(self):
#         return f"TakingCourses('{self.sid}', '{self.cid}')"


class Professors(db.Model):
    __tablename__ = "professors"
    pid = db.Column(db.String(10), db.ForeignKey('users.id'), primary_key=True)
    cid = db.Column(db.String(10), db.ForeignKey('courses.cid'), unique=True, nullable=False)
    group = db.relationship('Groups', backref='prof', lazy=True)
    forum = db.relationship('Forums', backref='creator', lazy=True)

    def __repr__(self):
        return f"Professors('{self.pid}', '{self.name}', '{self.cid}')"


# class PAccount(db.Model, UserMixin):
#     __tablename__ = "paccount"
#     __table_args__ = (
#         db.ForeignKeyConstraint(['pid', 'name'], ['professors.pid', 'professors.name']),
#     )
#     pid = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     account_id = db.Column(db.String(10), unique=True, nullable=False)
#     password = db.Column(db.String(60), nullable=False)
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

#     def get_id(self):
#         return (self.sid)

#     def __repr__(self):
#         return f"PAccount('{self.pid}', '{self.name}', '{self.account_id}', '{self.image_file}'"


# class PossibleTA(db.Model):
#     __tablename__ = "possibleta"
#     __table_args__ = (
#         db.ForeignKeyConstraint(['sid', 'cid'], ['takencourses.sid', 'takencourses.cid']),
#     )
#     sid = db.Column(db.Integer, primary_key=True)
#     cid = db.Column(db.String(10), primary_key=True)
#     ta = db.relationship('TeachingAssistants', backref='talist', lazy=True)

#     def __repr__(self):
#         return f"PossibleTA('{self.sid}', '{self.cid}')"


class TeachingAssistants(db.Model):
    __tablename__ = "teachingassistants"
    __table_args__ = (
        db.ForeignKeyConstraint(['sid', 'cid'], ['takencourses.sid', 'takencourses.cid']),
    )
    sid = db.Column(db.String(10), primary_key=True)
    cid = db.Column(db.String(10), primary_key=True)
    is_ta = db.Column(db.Boolean, nullable=False, server_default='0')
    

    def __repr__(self):
        return f"TeachingAssistants('{self.sid}', '{self.cid}', '{self.is_ta}')"


class Groups(db.Model):
    __tablename__ = "groups"
    gid = db.Column(db.Integer, primary_key=True)
    gname = db.Column(db.String(50), nullable=False)
    pid = db.Column(db.String(10), db.ForeignKey('professors.pid'), nullable=False)
    sid = db.Column(db.String(10), db.ForeignKey('students.sid'))
    groupinfo = db.relationship('GroupInfo', backref='groupinfo', lazy=True)
    group = db.relationship('ForumInfo', backref='group', lazy=True)

    def __repr__(self):
        return f"Groups('{self.gid}', '{self.gname}', '{self.pid}', '{self.sid}')"

class GroupInfo(db.Model):
    __tablename__ = "groupinfo"
    gid = db.Column(db.Integer, db.ForeignKey('groups.gid'), primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey('students.sid'), primary_key=True)

    def __repr__(self):
        return f"GroupInfo('{self.gid}', '{self.sid}', '{self.name}')"


class Forums(db.Model):
    __tablename__ = "forums"
    fid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    pid = db.Column(db.String(10), db.ForeignKey('professors.pid'), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    thread = db.relationship('Threads', backref='forum', lazy=True)
    foruminfo = db.relationship('ForumInfo', backref='info', lazy=True)

    def __repr__(self):
        return f"Forums('{self.gid}', '{self.sid}', '{self.name}')"


class ForumInfo(db.Model):
    __tablename__ = "foruminfo"
    fid = db.Column(db.Integer, db.ForeignKey('forums.fid', ondelete='CASCADE'), primary_key=True)
    gid = db.Column(db.Integer, db.ForeignKey('groups.gid'), primary_key=True)

    def __repr__(self):
        return f"ForumInfo: fid={self.fid} gid={self.gid}"

class Threads(db.Model):
    __tablename__ = "threads"
    fid = db.Column(db.Integer, db.ForeignKey('forums.fid', ondelete='CASCADE'), primary_key=True)
    tid = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(10), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    posts = db.relationship('Posts', backref='thread', lazy=True)
    # threadinfo = db.relationship('ThreadInfo', backref='info', lazy=True)

    def __repr__(self):
        return f"Threads: fid={self.fid} tid={self.tid} id={self.id} title={self.title} date_created={self.date_created}"


# class ThreadInfo(db.Model):
#     __tablename__ = "threadinfo"
#     fid = db.Column(db.Integer, db.ForeignKey('forums.fid', ondelete='CASCADE'), primary_key=True)
#     tid = db.Column(db.Integer, db.ForeignKey('threads.tid', ondelete='CASCADE'), primary_key=True)

#     def __repr__(self):
#         return f"ThreadInfo: fid={self.fid} tid={self.tid}"


class Posts(db.Model):
    __tablename__ = "posts"
    __table_args__ = (
        db.ForeignKeyConstraint(['fid', 'tid'], ['threads.fid', 'threads.tid'], ondelete='CASCADE'),
        db.ForeignKeyConstraint(['pfid', 'ptid', 'ppost_num'], ['posts.fid', 'posts.tid', 'posts.post_num']),
        db.CheckConstraint('pfid = fid'),
        db.CheckConstraint('ptid = tid'),
        db.CheckConstraint('ppost_num IS NULL OR ppost_num <> post_num'),    
    )
    fid = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.Integer, primary_key=True)
    post_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(10), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    rating = db.Column(db.Integer, db.CheckConstraint('rating >= 0 AND rating <= 10'), nullable=False, server_default='0')
    pfid = db.Column(db.Integer)
    ptid = db.Column(db.Integer)
    ppost_num = db.Column(db.Integer)

    def __repr__(self):
        return f"Posts: fid={self.fid} tid={self.tid} post_num={self.post_num} pfid={self.pfid}  ptid={self.ptid} ppost_num={self.ppost_num} id={self.id}  title={self.title} date={self.date_posted} rating={self.rating}"