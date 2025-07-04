-- Query repository recommendations from MotherDuck
-- Recommendations are generated based on topic analysis of starred repositories
-- Repositories are ranked by relevance and popularity
SELECT
    name,
    description,
    stars,
    language,
    url,
FROM recommendations
ORDER BY stars DESC