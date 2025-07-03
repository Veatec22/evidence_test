---
title: GitHub Portfolio & Technology Stack
description: Comprehensive showcase of my starred repositories, development stack, and technical interests through curated collections and detailed analysis.
queries:
  - starred.sql
---

```sql portfolio_overview
SELECT 
  COUNT(*) AS total_repos,
  COUNT(DISTINCT language) AS unique_languages,
  SUM(stars) AS total_stars,
  AVG(stars) AS avg_stars,
  SUM(forks) AS total_forks,
  COUNT(CASE WHEN is_curated = true THEN 1 END) AS curated_repos,
  COUNT(CASE WHEN archived = true THEN 1 END) AS archived_repos,
  COUNT(CASE WHEN fork = true THEN 1 END) AS forked_repos,
  COUNT(CASE WHEN last_release != 'No releases' THEN 1 END) AS active_projects,
  COUNT(DISTINCT CASE WHEN curated_tags != '' THEN curated_tags END) AS tag_combinations
FROM github.github_data_starred
```

```sql curated_stack_breakdown
SELECT 
  TRIM(tag_value) AS stack_category,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars,
  SUM(stars) AS total_stars,
  COUNT(DISTINCT language) AS languages_used,
  STRING_AGG(DISTINCT language, ', ' ORDER BY language) AS languages_list
FROM (
  SELECT *, UNNEST(string_split(curated_tags, ', ')) AS tag_value
  FROM github.github_data_starred
  WHERE curated_tags IS NOT NULL AND curated_tags != ''
)
GROUP BY stack_category
ORDER BY repo_count DESC
```

```sql language_mastery
SELECT 
  language,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars,
  SUM(stars) AS total_stars,
  COUNT(CASE WHEN is_curated = true THEN 1 END) AS curated_count,
  COUNT(CASE WHEN last_release != 'No releases' THEN 1 END) AS active_projects,
  ROUND(AVG(forks), 0) AS avg_forks
FROM github.github_data_starred
WHERE language IS NOT NULL AND language != 'Unknown'
GROUP BY language
ORDER BY repo_count DESC
LIMIT 15
```

```sql portfolio_highlights
SELECT 
  name,
  description,
  stars,
  forks,
  language,
  curated_tags,
  all_tags,
  last_release,
  url,
  is_curated
FROM github.github_data_starred
ORDER BY stars DESC
LIMIT 25
```

```sql core_development_stack
SELECT 
  name,
  description,
  stars,
  forks,
  language,
  curated_tags,
  last_release,
  url
FROM github.github_data_starred
WHERE curated_tags LIKE '%stack%'
ORDER BY stars DESC
LIMIT 15
```

```sql emerging_interests
SELECT 
  name,
  description,
  stars,
  language,
  curated_tags,
  created_at,
  url
FROM github.github_data_starred
WHERE curated_tags LIKE '%future-ideas%'
ORDER BY stars DESC
LIMIT 10
```

```sql recent_discoveries
SELECT 
  name,
  language,
  stars,
  forks,
  curated_tags,
  created_at,
  updated_at,
  url
FROM github.github_data_starred
WHERE created_at IS NOT NULL
ORDER BY created_at DESC
LIMIT 15
```

```sql topic_expertise
SELECT 
  TRIM(topic.value) AS expertise_area,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars,
  COUNT(CASE WHEN is_curated = true THEN 1 END) AS curated_count
FROM github.github_data_starred,
UNNEST(string_split(topics, ',')) AS topic
WHERE topics IS NOT NULL 
  AND topics != ''
  AND TRIM(topic.value) != ''
GROUP BY expertise_area
ORDER BY repo_count DESC
LIMIT 20
```

```sql project_activity_health
SELECT 
  CASE 
    WHEN last_release = 'No releases' THEN 'No Releases'
    WHEN last_release LIKE 'Error%' THEN 'Error'
    ELSE 'Actively Released'
  END AS activity_status,
  COUNT(*) AS repo_count,
  AVG(stars) AS avg_stars,
  COUNT(CASE WHEN is_curated = true THEN 1 END) AS curated_count
FROM github.github_data_starred
GROUP BY activity_status
```

```sql monthly_curation_trends
SELECT 
  DATE_TRUNC('month', CAST(created_at AS DATE)) AS month,
  COUNT(*) AS repos_added,
  COUNT(CASE WHEN is_curated = true THEN 1 END) AS curated_added,
  SUM(stars) AS stars_accumulated
FROM github.github_data_starred
WHERE created_at IS NOT NULL
GROUP BY month
ORDER BY month DESC
LIMIT 12
```

<Grid cols=4>
  <BigValue 
    data={portfolio_overview} 
    value=total_repos 
    title="Portfolio Size"
    description="Total starred repositories" 
  />
  <BigValue 
    data={portfolio_overview} 
    value=unique_languages 
    title="Technology Breadth"
    description="Programming languages" 
  />
  <BigValue 
    data={portfolio_overview} 
    value=curated_repos 
    title="Curated Stack"
    description="Personally organized repos" 
  />
  <BigValue 
    data={portfolio_overview} 
    value=total_stars 
    title="Community Impact"
    description="Total stars accumulated" 
  />
</Grid>

## 🚀 Technology Portfolio & Development Stack

This comprehensive dashboard showcases my GitHub starred repositories as both a **technical portfolio** and a **curated development stack**. It combines broad exploration of the open-source ecosystem with focused curation of tools and technologies I actively use or plan to explore.

<Tabs>
  <Tab label="🎯 Curated Stack">
    <div>
      <h3>My Development Ecosystem</h3>
      <p>Carefully curated repositories organized by purpose and development focus. These represent my core stack, tools I want to evaluate, and emerging technologies on my radar.</p>
    </div>
    
    <Grid cols=2>
      <BarChart 
        data={curated_stack_breakdown} 
        title="Stack Categories" 
        x="stack_category" 
        y="repo_count"
      />
      <BarChart 
        data={curated_stack_breakdown} 
        title="Quality by Category (Avg Stars)" 
        x="stack_category" 
        y="avg_stars"
      />
    </Grid>
    
    <div>
      <h4>📚 Core Development Stack</h4>
      <p>Essential tools and frameworks that form my primary development environment.</p>
      <DataTable 
        data={core_development_stack}
        search=true
        rows=15
      >
        <Column id="name" title="Repository" />
        <Column id="description" title="Description" />
        <Column id="stars" title="⭐ Stars" />
        <Column id="language" title="Language" />
        <Column id="curated_tags" title="Categories" />
        <Column id="url" title="Link" contentType="link" linkLabel="GitHub" />
      </DataTable>
    </div>
    
    <DataTable 
      data={curated_stack_breakdown}
      search=true
      rows=10
      title="Stack Category Overview"
    >
      <Column id="stack_category" title="Category" />
      <Column id="repo_count" title="Repository Count" />
      <Column id="avg_stars" title="Avg Quality (Stars)" fmt="num0" />
      <Column id="languages_used" title="Languages" />
      <Column id="languages_list" title="Language Details" />
    </DataTable>
  </Tab>
  
  <Tab label="💻 Language Expertise">
    <Grid cols=2>
      <BarChart 
        data={language_mastery} 
        title="Repository Count by Language" 
        x="language" 
        y="repo_count"
        swapXY=true
      />
      <BarChart 
        data={language_mastery} 
        title="Curated vs Total by Language" 
        x="language" 
        y="curated_count"
        y2="repo_count"
        swapXY=true
      />
    </Grid>
    
    <DataTable 
      data={language_mastery}
      search=true
      rows=15
      title="Programming Language Engagement"
    >
      <Column id="language" title="Language" />
      <Column id="repo_count" title="Total Repos" />
      <Column id="curated_count" title="Curated" />
      <Column id="avg_stars" title="Avg Stars" fmt="num0" />
      <Column id="active_projects" title="Active Projects" />
      <Column id="avg_forks" title="Avg Forks" />
    </DataTable>
  </Tab>
  
  <Tab label="🌟 Portfolio Highlights">
    <BarChart 
      data={portfolio_highlights} 
      title="Top Starred Repositories in Portfolio" 
      x="name" 
      y="stars"
      swapXY=true
    />
    
    <DataTable 
      data={portfolio_highlights}
      search=true
      rows=25
      title="Comprehensive Repository Portfolio"
    >
      <Column id="name" title="Repository" />
      <Column id="description" title="Description" />
      <Column id="stars" title="⭐ Stars" />
      <Column id="forks" title="🍴 Forks" />
      <Column id="language" title="Language" />
      <Column id="curated_tags" title="My Tags" />
      <Column id="is_curated" title="Curated" />
      <Column id="url" title="Link" contentType="link" linkLabel="View" />
    </DataTable>
  </Tab>
  
  <Tab label="🔮 Future & Trends">
    <Grid cols=2>
      <div>
        <h3>🧪 Emerging Interests</h3>
        <p>Technologies and projects I'm tracking for future exploration and learning.</p>
        <DataTable 
          data={emerging_interests}
          search=true
          rows=10
        >
          <Column id="name" title="Repository" />
          <Column id="description" title="Description" />
          <Column id="stars" title="⭐ Stars" />
          <Column id="language" title="Language" />
          <Column id="url" title="Link" contentType="link" linkLabel="Explore" />
        </DataTable>
      </div>
      
      <div>
        <h3>📅 Recent Discoveries</h3>
        <p>Latest repositories I've starred, showing current interests and learning direction.</p>
        <DataTable 
          data={recent_discoveries}
          search=true
          rows=15
        >
          <Column id="name" title="Repository" />
          <Column id="language" title="Language" />
          <Column id="stars" title="⭐ Stars" />
          <Column id="curated_tags" title="Categories" />
          <Column id="created_at" title="Starred Date" />
          <Column id="url" title="Link" contentType="link" linkLabel="View" />
        </DataTable>
      </div>
    </Grid>
    
    <LineChart 
      data={monthly_curation_trends} 
      title="Repository Curation Activity Over Time" 
      x="month" 
      y="repos_added"
      y2="curated_added"
    />
  </Tab>
  
  <Tab label="🎯 Expertise Areas">
    <Grid cols=2>
      <BarChart 
        data={topic_expertise} 
        title="GitHub Topic Engagement" 
        x="expertise_area" 
        y="repo_count"
        swapXY=true
      />
      
      <BarChart 
        data={project_activity_health} 
        title="Project Activity Health" 
        x="activity_status" 
        y="repo_count"
      />
    </Grid>
    
    <DataTable 
      data={topic_expertise}
      search=true
      rows=20
      title="Technical Expertise Areas (by GitHub Topics)"
    >
      <Column id="expertise_area" title="Topic/Skill Area" />
      <Column id="repo_count" title="Repository Count" />
      <Column id="avg_stars" title="Avg Stars" fmt="num0" />
      <Column id="curated_count" title="Curated" />
    </DataTable>
  </Tab>
</Tabs>

### 📊 Portfolio Insights

**Scale & Scope:**
- **<Value data={portfolio_overview} column=total_repos />** total repositories spanning **<Value data={portfolio_overview} column=unique_languages />** programming languages
- **<Value data={portfolio_overview} column=curated_repos />** personally curated repositories across **<Value data={portfolio_overview} column=tag_combinations />** different categories
- Combined community recognition: **<Value data={portfolio_overview} column=total_stars format="num0" />** stars

**Curation Quality:**
- **<Value data={portfolio_overview} column=active_projects />** repositories have active releases, indicating healthy project selection
- Average **<Value data={portfolio_overview} column=avg_stars format="num0" />** stars per repository shows focus on quality over quantity
- **<Value data={portfolio_overview} column=archived_repos />** archived repositories demonstrate awareness of project lifecycle

**Development Philosophy:**
This portfolio reflects a **balanced approach** between exploring the broader open-source ecosystem and maintaining a curated development stack. The combination of systematic curation with broad exploration demonstrates both **focused expertise** and **continuous learning**.

### 🔧 Technology Stack Categories

<Value data={curated_stack_breakdown} column=stack_category /> represents my most populated stack category with <Value data={curated_stack_breakdown} column=repo_count /> repositories, indicating my primary focus area. The curation spans multiple technology domains, showing versatility and comprehensive technical interests.

---

*This dashboard serves as both a **technical portfolio** showcasing my GitHub activity and a **living documentation** of my development stack, interests, and learning journey in the open-source ecosystem.*
