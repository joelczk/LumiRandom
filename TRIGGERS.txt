/*  Once a student's request to be a TA for a module is accepted, 
    remove all of that student's other requests to be a TA for other modules
    This is to prevent student from being more than 1 TA per semester
    (not good for studies -_-").
    Also checks if student is already a TA for a module, and reject further insertion. */
CREATE OR REPLACE FUNCTION remove_request()
RETURNS TRIGGER AS 
$content$ 
BEGIN
	IF (SELECT year FROM Students WHERE sid = NEW.sid) <= 1 OR
	NEW.cid NOT IN (SELECT cid FROM Professors) OR
	NOT EXISTS (
		SELECT *
		FROM TakenCourses
		WHERE sid = NEW.sid AND cid = NEW.cid AND grade LIKE 'A%'
	)
	THEN RETURN NULL;
	END IF;
	IF EXISTS (
		SELECT * 
		FROM TeachingAssistants
		WHERE sid = NEW.sid AND is_ta = True
	) THEN RETURN NULL;
	END IF;
	IF NEW.is_ta = True THEN
		DELETE FROM TeachingAssistants WHERE sid = NEW.sid AND is_ta = False;
	END IF;
	RETURN NEW;
END; 
$content$
LANGUAGE plpgsql;
CREATE TRIGGER delete_ta
BEFORE INSERT OR UPDATE ON TeachingAssistants
FOR EACH ROW
EXECUTE PROCEDURE remove_request();

/*After every new rating as long as rating > 0, then update is_rated = true */
CREATE OR REPLACE FUNCTION update_rated()
RETURNS TRIGGER AS $$ BEGIN
IF NEW.rating > 0 THEN
	NEW.is_rated = true;
ELSE 
	NEW.is_rated = false;
END IF;
RETURN NEW;
END;
$$LANGUAGE plpgsql;

CREATE TRIGGER update_rated
BEFORE UPDATE on takencourses
FOR EACH ROW EXECUTE PROCEDURE update_rated();

/* After a new thread is created, it also automatically becomes the first post of the thread, 
   since it is the thread topic for discussion. */
CREATE OR REPLACE FUNCTION add_post()
RETURNS TRIGGER AS 
$content$ 
BEGIN
	INSERT INTO Posts VALUES (NEW.fid, NEW.tid, 1, NEW.id, NEW.title, NEW.content, NEW.date_created, NULL, NULL, NULL, NULL);
	RETURN NULL;
END; 
$content$
LANGUAGE plpgsql;
CREATE TRIGGER new_thread
AFTER INSERT ON Threads
FOR EACH ROW
EXECUTE PROCEDURE add_post();



/* After the topic post (first post of the thread) has been edited, update also the thread title and content correspondingly */
CREATE OR REPLACE FUNCTION edit_thread()
RETURNS TRIGGER AS 
$content$ 
BEGIN
	IF NEW.post_num = 1 THEN
		UPDATE Threads
		SET title = NEW.title, content = NEW.content
		WHERE fid = NEW.fid AND tid = NEW.tid;
	END IF;
	RETURN NULL;
END; 
$content$
LANGUAGE plpgsql;
CREATE TRIGGER new_thread
AFTER UPDATE ON Posts
FOR EACH ROW
EXECUTE PROCEDURE edit_thread();
