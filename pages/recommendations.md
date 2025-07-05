---
title: Recommended GitHub Repositories
description: Curated repository recommendations based on your starred repositories, featuring high-quality projects with 1,000+ stars while filtering out ignored repositories.
queries:
  - recommendations.sql
---

```sql summary
SELECT 
  name,
  description,
  stars,
  language,
  url
FROM github.recommendations
ORDER BY stars DESC
```

```sql recommendation_stats
SELECT 
  COUNT(*) AS total_recommendations,
  COUNT(DISTINCT language) AS unique_languages,
  AVG(stars) AS avg_stars,
  SUM(stars) AS total_stars
FROM github.recommendations
```

```sql language_breakdown
SELECT 
  language,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars,
  SUM(stars) AS total_stars
FROM github.recommendations
WHERE language IS NOT NULL AND language != 'Unknown'
GROUP BY language
ORDER BY repo_count DESC
LIMIT 10
```

```sql top_recommendations
SELECT 
  name,
  description,
  stars,
  language,
  url
FROM github.recommendations
ORDER BY stars DESC
LIMIT 20
```

# 🎯 Recommended GitHub Repositories

This page displays **curated repository recommendations** based on your starred repositories. The recommendations feature high-quality projects with at least 1,000 stars, automatically filtering out repositories you've already starred and those in your ignore list.

## 📊 Recommendation Overview

<Grid cols=4>
  <BigValue 
    data={recommendation_stats} 
    value=total_recommendations 
    title="Total Recommendations"
    description="Curated suggestions for you" 
  />
  <BigValue 
    data={recommendation_stats} 
    value=unique_languages 
    title="Programming Languages"
    description="Technology diversity" 
  />
  <BigValue 
    data={recommendation_stats} 
    value=avg_stars 
    title="Average Stars"
    description="Quality indicator"
    fmt="num0"
  />
  <BigValue 
    data={recommendation_stats} 
    value=total_stars 
    title="Total Stars"
    description="Combined community recognition"
    fmt="num0"
  />
</Grid>

## 🌟 Top Recommendations

<DataTable 
  data={top_recommendations}
  search=true
  rows=20
  title="Highest Recommended Repositories"
>
  <Column id="name" title="Repository" />
  <Column id="description" title="Description" />
  <Column id="stars" title="⭐ Stars" />
  <Column id="language" title="Language" />
  <Column id="url" title="Link" contentType="link" linkLabel="View on GitHub" />
</DataTable>

## 📈 Analysis & Insights

<Tabs>
  <Tab label="🔍 All Recommendations">
    <DataTable 
      data={summary}
      search=true
      rows=50
      title="Complete Repository Recommendations"
    >
      <Column id="name" title="Repository" />
      <Column id="description" title="Description" />
      <Column id="stars" title="⭐ Stars" />
      <Column id="language" title="Language" />
      <Column id="url" title="Link" contentType="link" linkLabel="GitHub" />
    </DataTable>
  </Tab>
  
  <Tab label="💻 By Language">
    <BarChart 
      data={language_breakdown} 
      title="Recommendations by Programming Language" 
      x="language" 
      y="repo_count"
      swapXY=true
    />
    
    <DataTable 
      data={language_breakdown}
      search=true
      rows=10
      title="Language Distribution in Recommendations"
    >
      <Column id="language" title="Language" />
      <Column id="repo_count" title="Repository Count" />
      <Column id="avg_stars" title="Avg Stars" fmt="num0" />
      <Column id="total_stars" title="Total Stars" fmt="num0" />
    </DataTable>
  </Tab>
</Tabs>

---

### 🎯 How Recommendations Work

1. **Topic Analysis**: Analyzes topics from your starred repositories and curated lists
2. **Quality Filtering**: Only repositories with 1,000+ stars are considered
3. **Duplicate Removal**: Filters out repositories you've already starred
4. **Ignore List**: Automatically excludes repositories from your ignore list
5. **Ranking**: Results are ranked by popularity (stars)

*Recommendations are updated when you run the GitHub sync script, ensuring fresh suggestions based on your repository interests.* 