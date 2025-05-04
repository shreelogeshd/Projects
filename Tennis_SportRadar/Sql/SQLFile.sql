select * from categories;
select * from competitions;

-- 1. List all competitions along with their category name 
select a.competition_name,b.category_name from competitions a,categories b where a.category_id = b.category_id;

-- 2.Count the number of competitions in each category
SELECT b.category_name, COUNT(*) AS competition_count
FROM competitions a,categories b
where a.category_id = b.category_id
GROUP BY b.category_name;

-- 3.Find all competitions of type 'doubles'
select competition_name from competitions where type='doubles';

-- 4.Get competitions that belong to a specific category (e.g., ITF Men)
select a.competition_name from competitions a,categories b where a.category_id = b.category_id and b.category_name='ITF Men';

-- 5.Identify parent competitions and their sub-competitions
SELECT b.category_name AS parent_competition,a.competition_name AS sub_competition FROM competitions AS a
JOIN categories AS b ON a.category_id = b.category_id
ORDER BY b.category_name, a.competition_name;

-- 6.Analyze the distribution of competition types by category
SELECT b.category_name,a.type,COUNT(*) AS total_competitions FROM competitions as a
JOIN categories AS b ON a.category_id = b.category_id
GROUP BY b.category_name, a.type ORDER BY b.category_name, total_competitions DESC;

-- 7.List all competitions with no parent (top-level competitions)
select * from competitions where parent_id is null;

------------------------------------------------------

select * from complexes;
select * from venues;

-- 1.List all venues along with their associated complex name
select b.complex_name,a.venue_name,a.city_name,a.country_name from venues as a, complexes as b where a.complex_id= b.complex_id;

-- 2.Count the number of venues in each complex
select b.complex_name,count(*) as total_venues from complexes as b
join venues as a on a.complex_id= b.complex_id
group by b.complex_name order by b.complex_name desc;

-- 3.Get details of venues in a specific country (e.g., Chile)
select * from venues where country_name='Chile';

-- 4.Identify all venues and their timezones
select venue_name,city_name,country_name,timezone from venues;

-- 5.Find complexes that have more than one venue
select b.complex_name,count(*) as total_venues from complexes as b
join venues as a on a.complex_id= b.complex_id
group by b.complex_name having count(*) > 1;

-- 6.List venues grouped by country
SELECT country_name, COUNT(*) AS total_venues FROM venues
GROUP BY country_name ORDER BY total_venues DESC;

-- 7.Find all venues for a specific complex (e.g., Nacional)
select b.complex_name,a.venue_name,a.city_name,a.country_name from venues as a, complexes as b where a.complex_id= b.complex_id 
and b.complex_name='Kindarena';

---------------------------------------------------------

select * from competitors;
select * from competitor_rankings;

-- 1.Get all competitors with their rank and points.
select a.name,b.rank,b.points from competitors a, competitor_rankings b where a.competitor_id = b.competitor_id;

-- 2.Find competitors ranked in the top 5
select a.name,b.rank,b.points from competitors a, competitor_rankings b where a.competitor_id = b.competitor_id limit 5;

-- 3.List competitors with no rank movement (stable rank)
select a.name,b.rank,b.points from competitors a, competitor_rankings b where a.competitor_id = b.competitor_id and b.movement < 0;

-- 4. Get the total points of competitors from a specific country (e.g., Croatia)
select a.country,sum(b.points) as Total_points from competitors a, competitor_rankings b where a.competitor_id = b.competitor_id
group by a.country order by a.country asc;

-- 5. Count the number of competitors per country
select a.country, count(*) as total_competitors from competitors a, competitor_rankings b where a.competitor_id = b.competitor_id
group by a.country;

