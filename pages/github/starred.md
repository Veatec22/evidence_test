---
title: Starred GitHub Repositories
description: Analysis of my starred GitHub repositories with insights on languages, activity, and trends.
queries:
  - starred.sql
---

```sql total_stats
SELECT 
  COUNT(*) AS total_repos,
  COUNT(DISTINCT language) AS unique_languages,
  SUM(stars) AS total_stars,
  AVG(stars) AS avg_stars,
  SUM(forks) AS total_forks,
  COUNT(CASE WHEN archived = true THEN 1 END) AS archived_repos,
  COUNT(CASE WHEN fork = true THEN 1 END) AS forked_repos,
  COUNT(CASE WHEN last_release != 'No releases' THEN 1 END) AS repos_with_releases
FROM github.github_data_starred
```

```sql language_breakdown
SELECT 
  language,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars,
  SUM(stars) AS total_stars,
  AVG(forks) AS avg_forks,
  COUNT(CASE WHEN last_release != 'No releases' THEN 1 END) AS with_releases
FROM github.github_data_starred
WHERE language IS NOT NULL AND language != 'Unknown'
GROUP BY language
ORDER BY repo_count DESC
LIMIT 15
```

```sql top_starred_repos
SELECT 
  name,
  description,
  stars,
  forks,
  language,
  last_release,
  url
FROM github.github_data_starred
ORDER BY stars DESC
LIMIT 20
```

```sql recent_activity
SELECT 
  name,
  language,
  stars,
  forks,
  updated_at,
  pushed_at,
  url
FROM github.github_data_starred
WHERE pushed_at IS NOT NULL 
  AND pushed_at != ''
ORDER BY pushed_at DESC
LIMIT 15
```

```sql topic_analysis
SELECT 
  TRIM(topic.value) AS topic_name,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars
FROM github.github_data_starred,
UNNEST(SPLIT(topics, ',')) AS topic
WHERE topics IS NOT NULL 
  AND topics != ''
  AND TRIM(topic.value) != ''
GROUP BY topic_name
ORDER BY repo_count DESC
LIMIT 20
```

```sql release_activity
SELECT 
  CASE 
    WHEN last_release = 'No releases' THEN 'No Releases'
    WHEN last_release LIKE 'Error%' THEN 'Error'
    ELSE 'Has Releases'
  END AS release_status,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars
FROM github.github_data_starred
GROUP BY release_status
```

```sql monthly_stars
SELECT 
  DATE_TRUNC('month', CAST(created_at AS DATE)) AS month,
  COUNT(*) AS repos_starred,
  SUM(stars) AS total_stars_gained
FROM github.github_data_starred
WHERE created_at IS NOT NULL
GROUP BY month
ORDER BY month DESC
LIMIT 12
```

<Grid cols=4>
  <BigValue 
    data={total_stats} 
    value=total_repos 
    title="Total Repositories"
    description="Starred repositories" 
  />
  <BigValue 
    data={total_stats} 
    value=unique_languages 
    title="Programming Languages"
    description="Different languages used" 
  />
  <BigValue 
    data={total_stats} 
    value=total_stars 
    title="Total Stars"
    description="Combined stars of all repos" 
  />
  <BigValue 
    data={total_stats} 
    value=repos_with_releases 
    title="Active Projects"
    description="Repositories with releases" 
  />
</Grid>

## Repository Analysis

This dashboard provides insights into your starred GitHub repositories, helping you understand your development interests and the activity levels of projects you follow.

<Tabs>
  <Tab label="Language Distribution">
    <Grid cols=2>
      <BarChart 
        data={language_breakdown} 
        title="Repositories by Programming Language" 
        x="language" 
        y="repo_count"
        swapXY=true
      />
      <BarChart 
        data={language_breakdown} 
        title="Average Stars by Language" 
        x="language" 
        y="avg_stars"
        swapXY=true
      />
    </Grid>
    
    <DataTable 
      data={language_breakdown}
      search=true
      rows=10
    />
  </Tab>
  
  <Tab label="Top Repositories">
    <BarChart 
      data={top_starred_repos} 
      title="Most Starred Repositories" 
      x="name" 
      y="stars"
      swapXY=true
    />
    
    <DataTable 
      data={top_starred_repos}
      search=true
      rows=20
    >
      <Column id="name" title="Repository" />
      <Column id="description" title="Description" />
      <Column id="stars" title="⭐ Stars" />
      <Column id="forks" title="🍴 Forks" />
      <Column id="language" title="Language" />
      <Column id="last_release" title="Last Release" />
      <Column id="url" title="URL" contentType="link" linkLabel="View on GitHub" />
    </DataTable>
  </Tab>
  
  <Tab label="Activity & Topics">
    <Grid cols=2>
      <BarChart 
        data={topic_analysis} 
        title="Popular Topics" 
        x="topic_name" 
        y="repo_count"
        swapXY=true
      />
      
      <BarChart 
        data={release_activity} 
        title="Release Activity Distribution" 
        x="release_status" 
        y="repo_count"
      />
    </Grid>
    
    <div>
      <h3>Recently Active Repositories</h3>
      <DataTable 
        data={recent_activity}
        search=true
        rows=15
      >
        <Column id="name" title="Repository" />
        <Column id="language" title="Language" />
        <Column id="stars" title="⭐ Stars" />
        <Column id="pushed_at" title="Last Push" />
        <Column id="url" title="URL" contentType="link" linkLabel="View" />
      </DataTable>
    </div>
  </Tab>
  
  <Tab label="Trends">
    <LineChart 
      data={monthly_stars} 
      title="Repository Starring Activity Over Time" 
      x="month" 
      y="repos_starred"
    />
    
    <LineChart 
      data={monthly_stars} 
      title="Stars Accumulated Over Time" 
      x="month" 
      y="total_stars_gained"
    />
  </Tab>
</Tabs>

### Key Insights

**Repository Overview:**
- You have <Value data={total_stats} column=total_repos /> starred repositories
- These repos span <Value data={total_stats} column=unique_languages /> different programming languages
- Combined, they have <Value data={total_stats} column=total_stars format="num0" /> stars

**Activity Status:**
- <Value data={total_stats} column=repos_with_releases /> repositories have published releases
- <Value data={total_stats} column=archived_repos /> repositories are archived
- <Value data={total_stats} column=forked_repos /> are forks of other repositories
