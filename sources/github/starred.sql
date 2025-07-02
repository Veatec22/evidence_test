-- Query all starred repositories data from Google Sheets
SELECT 
    name,
    description,
    stars,
    forks,
    language,
    url,
    last_release,
    topics,
    created_at,
    updated_at,
    pushed_at,
    open_issues,
    archived,
    fork,
    fetched_at
FROM github.github_data_starred
ORDER BY stars DESC