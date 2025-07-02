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
FROM github_starred.StarredRepos_Sheet1
ORDER BY stars DESC