SELECT 
    b.primary_title,
    b.runtime_minutes,
    b.genres,
    r.average_rating,
    r.num_votes
FROM `bigquery-public-data.imdb.title_basics` b
    LEFT JOIN `bigquery-public-data.imdb.title_ratings` r USING (tconst)
WHERE 1=1
AND b.start_year >= EXTRACT(DAY FROM CURRENT_DATE('Poland'))
AND b.title_type = 'movie'