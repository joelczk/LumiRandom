CREATE TABLE Users (
	id 		VARCHAR(10) PRIMARY KEY,
	name	 	VARCHAR(100) NOT NULL,
	image_file 	VARCHAR(100) NOT NULL DEFAULT 'default.jpg',
	password 	VARCHAR(100) NOT NULL
);


CREATE TABLE Students (
	sid	 	VARCHAR(10) PRIMARY KEY REFERENCES Users(id),
	year	 	INTEGER NOT NULL CHECK (year >= 1 and year <= 5)	
);


CREATE TABLE Courses (
	cid	 	VARCHAR(10) PRIMARY KEY,
	cname 		VARCHAR(100) NOT NULL
);


CREATE TABLE TakenCourses (
	sid 	 	VARCHAR(10) REFERENCES Students,
	cid	 	VARCHAR(10) REFERENCES Courses,
	year 		VARCHAR(10) NOT NULL,
	sem	 	INTEGER NOT NULL CHECK (sem = 1 OR sem = 2),
	grade 		VARCHAR(5) DEFAULT NULL,
	rating 		INTEGER DEFAULT NULL,
	is_pending 	BOOLEAN NOT NULL DEFAULT FALSE,
	PRIMARY KEY 	(sid, cid)
	CHECK (rating IS NULL OR (rating >= 0 AND rating <= 10))
);


CREATE TABLE Professors (
	pid	 	VARCHAR(10) PRIMARY KEY REFERENCES Users(id),
	cid	 	VARCHAR(10) NOT NULL UNIQUE REFERENCES Courses(cid)
);


CREATE TABLE TeachingAssistants (
	sid	 	VARCHAR(10),
	cid	 	VARCHAR(10),
	is_ta 		BOOLEAN NOT NULL DEFAULT FALSE,
	PRIMARY KEY 	(sid, cid),
	FOREIGN KEY 	(sid, cid) REFERENCES TakenCourses(sid, cid)
);


CREATE TABLE Groups (
	gid 		INTEGER PRIMARY KEY,
	gname	 	VARCHAR(50) NOT NULL,
	pid	 	VARCHAR(10) NOT NULL REFERENCES Professors,
	sid 	 	VARCHAR(10),
	cid 		VARCHAR(10),
	FOREIGN KEY 	(sid, cid) REFERENCES TeachingAssistants(sid, cid),
	CHECK ((sid IS NOT NULL AND cid IS NOT NULL) OR (sid IS NULL AND cid IS NULL))
);


CREATE TABLE GroupInfo (
	gid	 	INTEGER REFERENCES Groups,
	sid	 	VARCHAR(10) REFERENCES Students,
	PRIMARY KEY 	(gid, sid)
);


CREATE TABLE Forums (
	fid	 	INTEGER PRIMARY KEY,
	title	 	VARCHAR(60) NOT NULL,
	pid 		VARCHAR(10) NOT NULL REFERENCES Professors,
	date_created 	TIMESTAMP NOT NULL
);


CREATE TABLE ForumInfo (
	fid 		INTEGER REFERENCES Forums,
	gid 		INTEGER REFERENCES Groups,
	PRIMARY KEY 	(fid, gid)
);


CREATE TABLE Threads (
	fid	 	INTEGER REFERENCES Forums ON DELETE CASCADE,
	tid 		INTEGER,
	id	 	VARCHAR(10) NOT NULL REFERENCES Users,
	title	 	VARCHAR(60) NOT NULL,
	content	 	TEXT NOT NULL,
	date_created 	TIMESTAMP NOT NULL,
	PRIMARY KEY 	(fid, tid)
);


CREATE TABLE Posts (
	fid	 	INTEGER,
	tid	 	INTEGER,
	post_num 	INTEGER,
	id 		VARCHAR(10) NOT NULL,
	title	 	VARCHAR(60) NOT NULL,
	content 	TEXT NOT NULL,
	date_posted 	TIMESTAMP NOT NULL,
	date_edited 	TIMESTAMP,
	pfid	 	INTEGER,
	ptid	 	INTEGER,
	ppost_num 	INTEGER,
	PRIMARY KEY 	(fid, tid, post_num),
	FOREIGN KEY 	(fid, tid) REFERENCES Threads(fid, tid) ON DELETE CASCADE,
	FOREIGN KEY 	(pfid, ptid, ppost_num) REFERENCES Posts(fid, tid, post_num) ON DELETE CASCADE,
	CHECK (pfid = fid),
	CHECK (ptid = tid),
	CHECK (ppost_num IS NULL OR ppost_num <> post_num)
);


CREATE TABLE Ratings (
	fid 		INTEGER,
	tid 		INTEGER,
	post_num 	INTEGER,
	id 		VARCHAR(10) REFERENCES Users,
	rating 		INTEGER NOT NULL CHECK (rating >=0 AND rating <= 5),
	PRIMARY KEY 	(fid, tid, post_num, id),
	FOREIGN KEY 	(fid, tid, post_num) REFERENCES Posts(fid, tid, post_num) ON DELETE CASCADE
);



<-- Set timezone for the current session to become GMT +8(Singapore/Asia) time -->
set timezone to 'GMT +8';
