CREATE TABLE IF NOT EXISTS city (
  id int NOT NULL,
  city_name varchar(255) NOT NULL,
  country varchar(255) NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS points_of_interest (
  POI_name varchar(255) NOT NULL,
  attraction_type varchar(255),
  description varchar(255),
  longitude float NOT NULL,
  latitude float NOT NULL,
  city_id int NOT NULL,
  PRIMARY KEY (POI_name)
);

CREATE TABLE IF NOT EXISTS photo (
  id SERIAL,
  url varchar(255) NOT NULL,
  date_taken Date,
  time_taken time,
  popularity int NOT NULL,
  depicted_POI_name varchar(255) NOT NULL,
  PRIMARY KEY (id)
);
