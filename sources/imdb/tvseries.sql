WITH episode_stats AS 
(
  SELECT
    parent_tconst,
    COUNT(*) AS episode_count,
    COUNT(DISTINCT season_number) = 1 AS is_debut  
    FROM `bigquery-public-data.imdb.title_episode`
  WHERE 1=1
    AND parent_tconst IS NOT NULL
  GROUP BY ALL
)

SELECT
  b.primary_title,
  b.start_year,
  b.runtime_minutes,
  b.genres,
  r.average_rating,
  r.num_votes,
  e.episode_count,
  e.season_count,
  e.first_season,
  e.last_season
FROM `bigquery-public-data.imdb.title_basics` b
JOIN episode_stats e ON b.tconst = e.parent_tconst
LEFT JOIN `bigquery-public-data.imdb.title_ratings` r USING (tconst)
WHERE 1=1
AND b.title_type = 'tvSeries'
AND b.start_year >= EXTRACT(DAY FROM CURRENT_DATE('Poland'))