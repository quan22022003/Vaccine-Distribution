drop table if exists vaccinetype cascade;
drop table if exists manufacturer cascade;
drop table if exists vaccinebatch cascade;
drop table if exists vaccinationstation cascade;
drop table if exists transportlog cascade;
drop table if exists staffmembers cascade;
drop table if exists shifts cascade;
drop table if exists patients cascade;
drop table if exists vaccinations cascade;
drop table if exists vaccinepatients cascade;
drop table if exists symptoms cascade;
drop table if exists diagnosis cascade;


create table vaccinetype(
	id varchar(50) primary key,
	name text not null,
	doses int not null,
	tempmin int not null,
	tempmax int not null
);

create table manufacturer(
	id varchar(10) primary key,
	country varchar(60) not null,
	phone varchar(20) not null,
	vaccine varchar(10) not null,
	foreign key (vaccine) references vaccinetype(id)
);

create table vaccinebatch(
	batchid varchar(10) primary key,
	type varchar(10) not null,
	amount int not null,
	manufacturer varchar(10) not null,
	manufdate date not null,
	expiration date not null,
	location varchar(100) not null,
	foreign key (manufacturer) references manufacturer(id),
	foreign key (type) references vaccinetype(id)
);

create table vaccinationstation(
	name varchar(100) primary key,
	address varchar(100) not null,
	phone varchar(20) not null
);

create table transportlog(
	batchid varchar(10) not null,
	arrival varchar(100) not null,
	departure varchar(100) not null,
	datearr date not null,
	datedep date not null,
	foreign key (batchid) references vaccinebatch(batchid),
	foreign key (arrival) references vaccinationstation(name),
	foreign key (departure) references vaccinationstation(name)
);

create table staffmembers(
	ssno varchar(100) primary key,
	name varchar(100) not null,
	dob date not null,
	phone varchar(50) not null,
	role varchar(10) check (role in ('doctor', 'nurse')),
	vaccstatus int check (vaccstatus in (0,1)),
	hospital varchar(100),
	foreign key (hospital) references vaccinationstation(name)
);

create table shifts(
	worker varchar(100),
	weekday varchar(20),
	station varchar(100),
	primary key (worker, weekday, station),
	foreign key (worker) references staffmembers(ssno),
	foreign key (station) references vaccinationstation(name)
);

create table patients(
	ssno varchar(100) primary key,
	name varchar(100) not null,
	dob date not null,
	gender varchar(1) check (gender in ('M', 'F'))
);

create table vaccinations(
	date date,
	location varchar(100),
	batchid varchar(10),
	primary key (date, location, batchid),
	foreign key (location) references vaccinationstation(name),
	foreign key (batchid) references vaccinebatch(batchid)
);

create table vaccinepatients(
	date date,
	location varchar(100),
	patientssno varchar(100),
	primary key (date, location, patientssno),
	foreign key (location) references vaccinationstation(name),
	foreign key (patientssno) references patients(ssno)
);

create table symptoms(
	name varchar(50) primary key,
	criticality int check (criticality in (0,1))
);

create table diagnosis(
	patient varchar(100),
	symptom varchar(50),
	date date,
	primary key (patient, symptom, date),
	foreign key (patient) references patients(ssno),
	foreign key (symptom) references symptoms(name)
);