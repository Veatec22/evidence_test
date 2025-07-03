---
title: GitHub Curated Lists
description: Analysis of repositories from curated GitHub lists (stack, nice-to-have, future-ideas) with tag-based organization.
queries:
  - lists.sql
---

```sql total_lists_stats
SELECT 
  COUNT(*) AS total_repos,
  COUNT(DISTINCT language) AS unique_languages,
  SUM(stars) AS total_stars,
  AVG(stars) AS avg_stars,
  SUM(forks) AS total_forks,
  COUNT(DISTINCT tags) AS unique_tag_combinations,
  AVG(tags_count) AS avg_tags_per_repo
FROM github.github_data_lists
```

```sql tag_breakdown
SELECT 
  TRIM(tag.value) AS tag_name,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars,
  SUM(stars) AS total_stars,
  COUNT(DISTINCT language) AS languages_count
FROM github.github_data_lists,
UNNEST(SPLIT(tags, ', ')) AS tag
WHERE tags IS NOT NULL AND tags != ''
GROUP BY tag_name
ORDER BY repo_count DESC
```

```sql language_by_tags
SELECT 
  language,
  TRIM(tag.value) AS tag_name,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars
FROM github.github_data_lists,
UNNEST(SPLIT(tags, ', ')) AS tag
WHERE language IS NOT NULL 
  AND language != '' 
  AND tags IS NOT NULL 
  AND tags != ''
GROUP BY language, tag_name
ORDER BY repo_count DESC
LIMIT 20
```

```sql top_repos_by_tag
SELECT 
  name,
  description,
  stars,
  forks,
  language,
  tags,
  url
FROM github.github_data_lists
ORDER BY stars DESC
LIMIT 15
```

```sql stack_focus
SELECT 
  name,
  description,
  stars,
  forks,
  language,
  url
FROM github.github_data_lists
WHERE tags LIKE '%stack%'
ORDER BY stars DESC
LIMIT 10
```

```sql multi_tag_repos
SELECT 
  name,
  tags,
  tags_count,
  stars,
  language,
  url
FROM github.github_data_lists
WHERE tags_count > 1
ORDER BY tags_count DESC, stars DESC
LIMIT 10
```

```sql recent_updates
SELECT 
  name,
  language,
  stars,
  tags,
  updated_at,
  url
FROM github.github_data_lists
WHERE updated_at IS NOT NULL 
  AND updated_at != ''
ORDER BY updated_at DESC
LIMIT 10
```

<Grid cols=4>
  <BigValue 
    data={total_lists_stats} 
    value=total_repos 
    title="Curated Repositories"
    description="From organized lists" 
  />
  <BigValue 
    data={tag_breakdown} 
    value=repo_count 
    title="Most Used Tag"
    description={tag_breakdown[0].tag_name}
  />
  <BigValue 
    data={total_lists_stats} 
    value=avg_tags_per_repo 
    title="Avg Tags per Repo"
    description="Tag density"
    fmt="num1"
  />
  <BigValue 
    data={total_lists_stats} 
    value=total_stars 
    title="Total Stars"
    description="Combined from all lists" 
  />
</Grid>

## Curated Repository Analysis

This dashboard analyzes repositories from your carefully curated GitHub lists, organized by tags that represent different categories: **stack** (core development tools), **nice-to-have** (useful additions), and **future-ideas** (experimental technologies).

<Tabs>
  <Tab label="Tag Overview">
    <Grid cols=2>
      <BarChart 
        data={tag_breakdown} 
        title="Repositories by Tag" 
        x="tag_name" 
        y="repo_count"
      />
      <BarChart 
        data={tag_breakdown} 
        title="Average Stars by Tag" 
        x="tag_name" 
        y="avg_stars"
      />
    </Grid>
    
    <DataTable 
      data={tag_breakdown}
      search=true
      rows=10
    >
      <Column id="tag_name" title="Tag" />
      <Column id="repo_count" title="Repository Count" />
      <Column id="avg_stars" title="Avg Stars" fmt="num0" />
      <Column id="total_stars" title="Total Stars" fmt="num0" />
      <Column id="languages_count" title="Languages" />
    </DataTable>
  </Tab>
  
  <Tab label="Stack Focus">
    <div>
      <h3>Core Development Stack</h3>
      <p>These are the essential tools and technologies in your development stack.</p>
    </div>
    
    <BarChart 
      data={stack_focus} 
      title="Stack Repositories by Stars" 
      x="name" 
      y="stars"
      swapXY=true
    />
    
    <DataTable 
      data={stack_focus}
      search=true
      rows=10
    >
      <Column id="name" title="Repository" />
      <Column id="description" title="Description" />
      <Column id="stars" title="⭐ Stars" />
      <Column id="forks" title="🍴 Forks" />
      <Column id="language" title="Language" />
      <Column id="url" title="URL" contentType="link" linkLabel="View on GitHub" />
    </DataTable>
  </Tab>
  
  <Tab label="Top Repositories">
    <BarChart 
      data={top_repos_by_tag} 
      title="Most Starred Curated Repositories" 
      x="name" 
      y="stars"
      swapXY=true
    />
    
    <DataTable 
      data={top_repos_by_tag}
      search=true
      rows=15
    >
      <Column id="name" title="Repository" />
      <Column id="description" title="Description" />
      <Column id="stars" title="⭐ Stars" />
      <Column id="tags" title="Tags" />
      <Column id="language" title="Language" />
      <Column id="url" title="URL" contentType="link" linkLabel="View on GitHub" />
    </DataTable>
  </Tab>
  
  <Tab label="Cross-Tag Analysis">
    <Grid cols=2>
      <div>
        <h3>Multi-Tagged Repositories</h3>
        <p>Repositories that appear in multiple lists, indicating cross-category relevance.</p>
        <DataTable 
          data={multi_tag_repos}
          search=true
          rows=10
        >
          <Column id="name" title="Repository" />
          <Column id="tags" title="Tags" />
          <Column id="tags_count" title="Tag Count" />
          <Column id="stars" title="⭐ Stars" />
          <Column id="url" title="URL" contentType="link" linkLabel="View" />
        </DataTable>
      </div>
      
      <div>
        <h3>Language Distribution by Tag</h3>
        <DataTable 
          data={language_by_tags}
          search=true
          rows=15
        >
          <Column id="language" title="Language" />
          <Column id="tag_name" title="Tag" />
          <Column id="repo_count" title="Count" />
          <Column id="avg_stars" title="Avg Stars" fmt="num0" />
        </DataTable>
      </div>
    </Grid>
  </Tab>

  <Tab label="Recent Activity">
    <div>
      <h3>Recently Updated Repositories</h3>
      <p>Most recently updated repositories from your curated lists.</p>
    </div>
    
    <DataTable 
      data={recent_updates}
      search=true
      rows=10
    >
      <Column id="name" title="Repository" />
      <Column id="language" title="Language" />
      <Column id="stars" title="⭐ Stars" />
      <Column id="tags" title="Tags" />
      <Column id="updated_at" title="Last Updated" />
      <Column id="url" title="URL" contentType="link" linkLabel="View" />
    </DataTable>
  </Tab>
</Tabs>

### Key Insights

**Curation Overview:**
- You have <Value data={total_lists_stats} column=total_repos /> repositories across your curated lists
- These span <Value data={total_lists_stats} column=unique_languages /> different programming languages
- Average of <Value data={total_lists_stats} column=avg_tags_per_repo fmt="num1" /> tags per repository

**Tag Distribution:**
- **<Value data={tag_breakdown} column=tag_name />** is your most populated tag with <Value data={tag_breakdown} column=repo_count /> repositories
- Multi-tagged repositories indicate tools with cross-functional utility
- Core stack repositories represent your established development foundation

**Quality Metrics:**
- Combined star count: <Value data={total_lists_stats} column=total_stars format="num0" />
- Average stars per repository: <Value data={total_lists_stats} column=avg_stars format="num0" />
- This indicates a curated selection of high-quality, well-regarded tools