SELECT
  name,
  description,
  stars,
  forks,
  language,
  url,
  topics,
  score
FROM github.github_data_recommendations
ORDER BY score DESC 