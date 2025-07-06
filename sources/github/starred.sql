SELECT 
    name,
    stars,
    language,
    url,
    last_release,
    curated_tags,
    categories,
    all_tags,
    is_curated,
FROM starred
ORDER BY stars DESC