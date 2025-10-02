CREATE TABLE agency(
    agency_id VARCHAR NOT NULL,
    agency_name VARCHAR NOT NULL,
    agency_url VARCHAR NOT NULL,
    agency_timezone VARCHAR NOT NULL,
    agency_lang VARCHAR,
    agency_phone VARCHAR,
    agency_fare_url VARCHAR,
    agency_email VARCHAR,
    CONSTRAINT agency_pk PRIMARY KEY (agency_id)
);


CREATE TABLE calendar (
    service_id VARCHAR NOT NULL,
    monday VARCHAR NOT NULL,
    tuesday VARCHAR NOT NULL,
    wednesday VARCHAR NOT NULL,
    thursday VARCHAR NOT NULL,
    friday VARCHAR NOT NULL,
    saturday VARCHAR NOT NULL,
    sunday VARCHAR NOT NULL,
    start_date VARCHAR NOT NULL,
    end_date VARCHAR NOT NULL,
    CONSTRAINT calendar_pk PRIMARY KEY (service_id)
);


CREATE TABLE calendar_dates (
    service_id VARCHAR NOT NULL,
    date VARCHAR NOT NULL,
    exception_type INTEGER NOT NULL,
    CONSTRAINT calendar_fk FOREIGN KEY (service_id) REFERENCES calendar(service_id)
);


# pas de pk dans feed_info
CREATE TABLE feed_info (
    feed_publisher_name VARCHAR NOT NULL,
    feed_publisher_url VARCHAR NOT NULL,
    feed_lang VARCHAR NOT NULL,
    default_lang VARCHAR,
    feed_start_date VARCHAR NOT NULL,
    feed_end_date VARCHAR NOT NULL
);


CREATE TABLE routes(
    route_id VARCHAR NOT NULL,
    agency_id VARCHAR NOT NULL,
    route_short_name VARCHAR NOT NULL,
    route_long_name VARCHAR NOT NULL,
    route_desc VARCHAR,
    route_type VARCHAR NOT NULL,
    route_url VARCHAR,
    route_color VARCHAR,
    route_text_color VARCHAR,
    route_sort_order INTEGER,
    CONSTRAINT route_pk PRIMARY KEY (route_id),
    CONSTRAINT agency_fk FOREIGN KEY (agency_id) REFERENCES agency(agency_id)
);


CREATE TABLE shapes(
    shape_id VARCHAR NOT NULL,
    shape_pt_lat VARCHAR NOT NULL,
    shape_pt_lon VARCHAR NOT NULL,
    shape_pt_sequence INTEGER NOT NULL,
    shape_dist_traveled DOUBLE,
    CONSTRAINT shapes_pk PRIMARY KEY (shape_id, shape_pt_sequence)
);


CREATE TABLE stops(
    stop_id VARCHAR NOT NULL,
    stop_code VARCHAR,
    stop_name VARCHAR NOT NULL,
    stop_lat VARCHAR NOT NULL,
    stop_lon VARCHAR NOT NULL,
    zone_id VARCHAR NOT NULL,
    location_type VARCHAR,
    parent_station VARCHAR NOT NULL,
    stop_timezone VARCHAR,
    wheelchair_boarding VARCHAR,
    CONSTRAINT stops_pk PRIMARY KEY (stop_id)
);


CREATE TABLE trips(
    route_id VARCHAR NOT NULL,
    service_id VARCHAR NOT NULL,
    trip_id VARCHAR NOT NULL,
    trip_headsign VARCHAR,
    trip_short_name VARCHAR,
    direction_id VARCHAR,
    shape_id VARCHAR NOT NULL,
    wheelchair_accessible VARCHAR,
    bikes_allowed VARCHAR,
    CONSTRAINT trips_pk PRIMARY KEY (trip_id),
    CONSTRAINT route_fk FOREIGN KEY (route_id) REFERENCES routes(route_id),
    CONSTRAINT calendar_fk2 FOREIGN KEY (service_id) REFERENCES calendar(service_id)
);



CREATE TABLE stop_times(
    trip_id VARCHAR NOT NULL,
    arrival_time VARCHAR NOT NULL,
    departure_time VARCHAR NOT NULL,
    stop_id VARCHAR NOT NULL,
    stop_sequence INTEGER NOT NULL,
    pickup_type VARCHAR,
    drop_off_type VARCHAR,
    CONSTRAINT stop_times_pk PRIMARY KEY (trip_id, stop_sequence),
    CONSTRAINT trip_fk FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    CONSTRAINT stop_fk FOREIGN KEY (stop_id) REFERENCES stops(stop_id),
);
