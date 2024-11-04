--Tables
CREATE TABLE uploaded_image (
	uploaded_image_id serial NOT NULL,
	uploaded_image_user_id int4 NOT NULL,
	uploaded_image_file_name varchar(128) NOT NULL,
	uploaded_image_created_datetime timestamp NOT NULL,
	uploaded_image_modified_datetime timestamp NOT NULL,
	uploaded_image_status_id int2 NOT NULL,
    uploaded_image_detection_id int2 NULL,
    uploaded_image_gps_location_latitude float8 NOT NULL,
    uploaded_image_gps_location_longitude float8 NOT NULL,
	CONSTRAINT uploaded_image_pk PRIMARY KEY (uploaded_image_id)
);
CREATE TABLE uploaded_image_status (
	uploaded_image_status_id serial NOT NULL,
	uploaded_image_status_name varchar(64) NOT NULL,
	CONSTRAINT uploaded_image_status_pk PRIMARY KEY (uploaded_image_status_id)
);
CREATE TABLE "user" (
	user_id serial NOT NULL,
	user_name varchar(128) NOT NULL,
	user_login varchar(64) NOT NULL,
	user_password varchar(256) NOT NULL,
	user_role_id int2 NOT NULL,
	user_created_datetime timestamp NOT NULL,
	user_modified_datetime timestamp NULL,
	user_auth_token TEXT NOT NULL,
	user_email varchar(64) NOT NULL,
	user_phone_number varchar(18) NULL,
	ADD CONSTRAINT unique_user_email UNIQUE (user_email);
	CONSTRAINT user_pk PRIMARY KEY (user_id)
);
CREATE TABLE user_role (
	user_role_id serial NOT NULL,
	user_role_name varchar(64) NOT NULL,
	CONSTRAINT user_role_pk PRIMARY KEY (user_role_id)
);
CREATE TABLE detection (
	detection_id serial NOT NULL,
	detection_name varchar(64) NOT NULL,
	CONSTRAINT detection_pk PRIMARY KEY (detection_id),
	CONSTRAINT detection_unique UNIQUE (detection_name)
);

--Constraints
ALTER TABLE uploaded_image
ADD CONSTRAINT fk_uploaded_image_detection_id
FOREIGN KEY (uploaded_image_detection_id)
REFERENCES detection (detection_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

ALTER TABLE uploaded_image
ADD CONSTRAINT fk_uploaded_image_status_id
FOREIGN KEY (uploaded_image_status_id)
REFERENCES uploaded_image_status (uploaded_image_status_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

ALTER TABLE uploaded_image
ADD CONSTRAINT fk_uploaded_image_user_id
FOREIGN KEY (uploaded_image_user_id)
REFERENCES "user" (user_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

ALTER TABLE "user"
ADD CONSTRAINT fk_user_role_id
FOREIGN KEY (user_role_id)
REFERENCES user_role (user_role_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

ALTER TABLE "user"
ADD CONSTRAINT user_login_unique UNIQUE (user_login);

--Indexes
CREATE INDEX idx_uploaded_image_gps ON uploaded_image (uploaded_image_gps_location_latitude, uploaded_image_gps_location_longitude);
CREATE INDEX idx_uploaded_image_status_id ON uploaded_image (uploaded_image_status_id);
CREATE INDEX idx_uploaded_image_detection_id ON uploaded_image (uploaded_image_detection_id);
CREATE INDEX idx_uploaded_image_user_id ON uploaded_image (uploaded_image_user_id);

--Functions
CREATE OR REPLACE FUNCTION update_user_modified_datetime()
RETURNS TRIGGER AS $$
BEGIN
    NEW.user_modified_datetime = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_modified_datetime
BEFORE UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION update_user_modified_datetime();

--Inserts
INSERT INTO user_role (user_role_id, user_role_name) VALUES(1, 'Admin');
INSERT INTO user_role (user_role_id, user_role_name) VALUES(2, 'Reporter');

INSERT INTO "user" (user_id, user_name, user_login, user_password, user_role_id, user_auth_token, user_email) VALUES(1, 'Test Admin', 'admin', '$2b$12$8888x04F81Br/t5xGbKnx.M1zfB58sM.DxEAGgd5Ic4xwp3BCzUj.', 1, 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNzY1MDY4OSwianRpIjoiNGY1NzI1YmItMjUzOS00NzZhLWI2ZDItNTdkNjlmYmU1N2MzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzI3NjUwNjg5LCJjc3JmIjoiMTk5ZDU4OTItYmY4OC00MGVjLTgxZTMtY2IwMzQxMThjMTY1IiwiZXhwIjoxNzI3NjUxNTg5fQ.Nqj2OV4sxSA4A7BRzvSjOZNl0FbB9AIt8CBrfFM_-P8', 'testadmin@gmail.com');

INSERT INTO uploaded_image_status (uploaded_image_status_id, uploaded_image_status_name) VALUES(1, 'UPLOADED');
INSERT INTO uploaded_image_status (uploaded_image_status_id, uploaded_image_status_name) VALUES(2, 'DETECTED');
INSERT INTO uploaded_image_status (uploaded_image_status_id, uploaded_image_status_name) VALUES(3, 'PROCESSED');

INSERT INTO detection (detection_id, detection_name) VALUES(1, 'POTHOLE');
