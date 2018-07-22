# EventLogApi Setup

Event Log API Setup Documentation

Designed & Developed By	Date	Significant Modules
Jagadisa Padhy	22/7/2018	Python Flask Framework, Flask Restful API, MySql Database



Table of Contents:
1.	Python Setup Instructions ………………………………………..
2.	MySQL Setup …………………………………………………………….
3.	Flask Setup ………………………………………………………………..
4.	MySQL Connection Setup …………………………………………







1.	Python Setup Instructions:
Instructions
Please follow the instructions in the order specified as below:

•	Install Python 2.7.10
•	Update PIP to 10.0.1 with below command:
	python –m pip install pip==10.0.1
•	Install the following modules with pip:
pip install Module==Version(Ex: Module= flask and Version=1.0.2)
OR
python –m pip install Module==Version(Ex: Module= flask and Version=1.0.2)

Modules 		    Version

flask               1.0.2
flask-restful       0.3.6
flask-mysql         1.4.0



2.	MySQL Setup Instructions:

All Tables, Store Procedures and Triggers written with MySQL 5.7.22. The Following are the queries to create database, table, stored procedure and trigger for EventLogApi.
Open MySQL Shell and create with following commands:


•	mysql -u root -p

•	CREATE DATABASE ‘event’;
•	USE event;
•	This is master table to keep event records. This table will help for identify no. of events data we are keeping.

CREATE TABLE `event_master` (
  `idevent_master` int(11) NOT NULL AUTO_INCREMENT,
  `event_name` varchar(128) NOT NULL,
  `event_code` varchar(128) NOT NULL,
  `status` tinyint(4) NOT NULL,
  PRIMARY KEY (`idevent_master`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;



•	This table is designed to keep all event details records in both structured and un-structured data. Unstructured data will keep in json format. So that we can any custom data based on event type. This table is dependent to event_master table for event type.

CREATE TABLE `event_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `noun` varchar(45) NOT NULL,
  `verb` varchar(45) NOT NULL,
  `event_id_fk` int(11) NOT NULL,
  `event_data` json DEFAULT NULL,
  `event_date` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `event_source` varchar(256) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_event_master_event_details_id_idx` (`event_id_fk`),
  CONSTRAINT `fk_event_master_event_details_id` FOREIGN KEY (`event_id_fk`) REFERENCES `event_master` (`idevent_master`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



•	This table is designed to keep all alert record which are inserting based on some event type condition. One Column “alert_status” can be used for different alert status. Presently I am keeping status like ‘pending/sent’ during insertion. Currently data is inserting this table is based on “login-failed” event of any user is failing more than and equals to 5 times within 10 minutes. 

CREATE TABLE `alert_log` (
  `idalert_log` int(11) NOT NULL AUTO_INCREMENT,
  `event_details_fk` int(11) NOT NULL,
  `alert_status` varchar(45) NOT NULL,
  PRIMARY KEY (`idalert_log`),
  KEY `fk_alert_event_details_id` (`event_details_fk`),
  CONSTRAINT `fk_event_master_event_details` FOREIGN KEY (`event_details_fk`) REFERENCES `event_details` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


•	This stored procedure is designed to inset all data into “event_details” table.
CREATE PROCEDURE `sp_insertEvent`(data JSON)
BEGIN

DECLARE noun varchar(128);
DECLARE verb varchar(128);
DECLARE event_type varchar(128);
DECLARE eventId int;
DECLARE Id int;
DECLARE event_data JSON;
DECLARE event_date timestamp;


set @noun=replace(JSON_EXTRACT(data,'$.noun'), '"', '');
set @verb=replace(JSON_EXTRACT(data,'$.verb'), '"', '');
set @event_type= replace(JSON_EXTRACT(data,'$.eventId'), '"', '');
set @event_data=JSON_EXTRACT(data,'$.data');
set @event_date=replace(JSON_EXTRACT(data,'$.timestamp'), '"', '');


#select UNIX_TIMESTAMP(@event_date);
select @eventId:=idevent_master from event.event_master where event_code=@event_type;

#select @noun,@verb,@eventId,@event_data,STR_TO_DATE(@event_date, '%Y-%m-%d %H:%i:%s');
#select @Id:=count(*)+1 from event.event_details;

INSERT INTO event.event_details (noun,verb,event_id_fk,event_data,event_date,event_source)VALUES (@noun,@verb,@eventId,@event_data, STR_TO_DATE(@event_date, '%Y-%m-%d %H:%i:%s'),'');   

END

•	This trigger is designed to insert data into “alert_log” table on insert event of “event_details” table. Data insertion will happen if user is failing to login more than and equals to 5 times within 10 minutes.

DELIMITER $$

CREATE TRIGGER insert_alert_log
    AFTER INSERT ON event_details
    FOR EACH ROW 
BEGIN

    DECLARE userName varchar(128);
    DECLARE recCount INT DEFAULT 6;
    DECLARE event_type varchar(128);
    select event_code INTO @event_type from event_master where idevent_master=NEW.event_id_fk;
    IF @event_type = 'login-failed'
	THEN
    set @userName = JSON_EXTRACT(NEW.event_data,'$.user.name'); 
     
    select count(*) INTO @recCount from event.event_details where event_date<=NEW.event_date and event_date>=NEW.event_date - INTERVAL 10 MINUTE and JSON_CONTAINS(event_data, @userName,'$.user.name');
    IF @recCount>5
    THEN
		INSERT INTO alert_log (event_details_fk,alert_status) VALUES(NEW.id,'pending');
    END IF;    
	end if;
END$$
DELIMITER ;



3.	API Setup Instructions:

Download code from GIT. Please follow the fillowing instructions to setup API and start server.
•	GIT base path: https://github.com/jagadish4893/EventLogApi.git 
•	Open config.py file from “EventLogApi” Directory and do mysql connection changes.
•	Open Command prompt. 
•	Go to “EventLogApi” Directory with cd command.
•	Run the below command:
	python event_api.py

•	Run the below command to call Api to insert Event Log.
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"noun": "user-login",   "verb": "failed",  "eventId": "login-failed",   "timestamp": "2018-07-22 12:25:29.000000",   "data": {     "id": 1,    "user": {      "id": 2,      "name": "Admin"    }  }}' \
  http://127.0.0.1:5000/AddEventLog



