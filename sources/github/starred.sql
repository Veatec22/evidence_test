-- Query unified starred repositories data from MotherDuck
-- Combines all starred repos with detailed GitHub data and curated list tags
-- This serves as both a portfolio showcase and comprehensive repository analysis
SELECT 
    name,
    description,
    stars,
    language,
    url,
    last_release,
    curated_tags,
    all_tags,
    is_curated,
FROM starred
ORDER BY stars DESC