--query 1
select s.ssno, s.name, s.phone, s.role, s.vaccstatus, v.location 
from staffmembers s join shifts s2 on s.ssno = s2.worker 
join vaccinations v on v.location = s2.station
where v.date = '2021-05-10' and trim(lower(to_char(timestamp '2021-05-10','DAY'))) = lower(s2.weekday);

--query 2
select s.ssno, s.name, s.dob, s.phone, s.phone, s.role, s.vaccstatus, s.hospital
from staffmembers s 
join shifts sh on sh.worker = s.ssno
join vaccinationstation st on st.name = sh.station
where sh.weekday = 'Wednesday' and st.address like '%HELSINKI%' and s.role = 'doctor';

--query 3
--all vaccine batches
select b1.batchid, b1.location as currentLocation, b2.lastlocation
join (select t.batchid, t.arrival as lastlocation, t.datearr
        from transportlog t
        inner join (select batchid, max(tlog1.datearr) as latestdatearr
                        from transportlog as tlog1
                        group by batchid) as t2 on t.datearr = t2.latestdatearr
        where t.batchid = t2.batchid) as b2 on b1.batchid = b2.batchid
join vaccinationstation as vs on b2.lastlocation = vs.name
order by b1.location != b2.lastlocation, b1.batchid;

--inconsistent location
select b1.batchid, b1.location as currentLocation, b2.lastlocation, vs.phone
from vaccinebatch as b1
join (select t.batchid, t.arrival as lastlocation, t.datearr
        from transportlog t
        inner join (select batchid, max(tlog1.datearr) as latestdatearr
                        from transportlog as tlog1
                        group by batchid) as t2 on t.datearr = t2.latestdatearr
        where t.batchid = t2.batchid) as b2 on b1.batchid = b2.batchid
join vaccinationstation as vs on b2.lastlocation = vs.name
where b1.location != b2.lastlocation
order by b1.batchid;

--query 4
select p.patientssNo, p.date, p.location, v.batchid, b."type" 
from vaccinepatients p join diagnosis d on p.patientssNo = d.patient 
join symptoms s on s.name = d.symptom
join vaccinations v on v.date = p.date and v.location = p.location
join vaccinebatch b on b.batchid = v.batchid 
where s.criticality = '1' and d.date >= '2021-05-10';

--query 5
create or replace view Patients_vaccStat as

	select ssno, p.name, dob, gender, 1 as vaccinationStatus from patients p 
	join vaccinepatients v on p.ssNo = v.patientssno,
	vaccinations v2, vaccinebatch v3, vaccinetype v4
	where v."location" = v2."location" and v."date" = v2.date and v2.batchid = v3.batchid and v3.type = v4.id
	group by ssno, doses
	having count(ssno) = doses
	
	union 
	
	(select *, 0 as vaccinationStatus from patients 
	except 
	(
	select ssno, p.name, dob, gender, 0 as vaccinationStatus from patients p 
	join vaccinepatients v on p.ssNo = v.patientssno,
	vaccinations v2, vaccinebatch v3, vaccinetype v4
	where v."location" = v2."location" and v."date" = v2.date and v2.batchid = v3.batchid and v3.type = v4.id
	group by ssno, doses
	having count(ssno) = doses));
	
--query 6
select v.location, sum(case when v.type = 'V01' then v.amount else 0 end) as type_V01, 
sum(case when v.type = 'V02' then v.amount else 0 end) as type_V02,
sum(case when v.type = 'V03' then v.amount else 0 end) as type_V03, sum(v.amount)
from vaccinebatch v 
group by v.location
order by v.location;

--query 7
select b.type, d.symptom, round((count(patient):: decimal)/(total.sum),3) as average_frequency
from vaccinepatients p 
join diagnosis d on p.patientssno = d.patient
join vaccinations v on p.date = v.date and p.location = v.location
join vaccinebatch b on b.batchid = v.batchid
join (select count(patientssno) as sum, b.type
		from vaccinations v join vaccinebatch b on b.batchid = v.batchid
		join vaccinepatients p on v.date = p.date and v.location = p.location
		group by b.type) as total on total.type = b.type
where d.date >= v.date
group by b.type, d.symptom, total.sum;
