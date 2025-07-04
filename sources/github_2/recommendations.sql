-- Query repository recommendations from MotherDuck
-- Recommendations are generated based on topic analysis of starred repositories
-- Repositories are ranked by relevance and popularity
SELECT
    name,
    description,
    stars,
    forks,
    language,
    url,
    topics,
    matched_topics,
    topic_frequency_score,
    num_topic_matches
FROM recommendations
ORDER BY topic_frequency_score DESC, stars DESC