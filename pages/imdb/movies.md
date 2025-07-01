---
title: IMDB Movies
description: Analysis of IMDB movie data from this year.
queries:
  - movies.sql
---

```sql total_movies
SELECT 
  COUNT(*) AS total_count,
  COUNT(DISTINCT genres) AS unique_genres,
  SUM(runtime_minutes) AS total_runtime_minutes,
  AVG(runtime_minutes) AS average_runtime_minutes,
  SUM(num_votes) AS total_votes,
  AVG(average_rating) AS average_rating
FROM movies
```

```sql genre_analysis
SELECT 
  TRIM(genre) AS genre_name,
  COUNT(*) AS count
FROM movies,
UNNEST(SPLIT(genres, ',')) AS genre
WHERE genre IS NOT NULL AND TRIM(genre) != ''
GROUP BY genre_name
ORDER BY count DESC
LIMIT 15
```

```sql movies_table
SELECT primary_title, runtime_minutes, genres, average_rating, num_votes
FROM movies
LIMIT 100
```

```sql yearly_genre_breakdown
SELECT 
  TRIM(genre) AS genre_name,
  COUNT(*) AS count
FROM movies,
UNNEST(SPLIT(genres, ',')) AS genre
WHERE genre IS NOT NULL AND TRIM(genre) != ''
GROUP BY ALL
ORDER BY count DESC
```

<BigValue data={total_movies} value=total_count description="Total Movies from 2025+" />
<BigValue data={total_movies} value=unique_genres description="Unique Genres" />
<BigValue data={total_movies} value=total_runtime_minutes description="Total Runtime Minutes" />
<BigValue data={total_movies} value=average_runtime_minutes description="Average Runtime Minutes" />
<BigValue data={total_movies} value=total_votes description="Total Votes" />
<BigValue data={total_movies} value=average_rating description="Average Rating" />

## Movie Industry Analysis (2025+)

This analysis examines upcoming and recently released movies from 2025 onwards, providing insights into genre trends and release patterns in the modern film industry.

<Tabs fullWidth=true>
    <Tab label="Overview Charts">
        <Grid cols=2>

          <BarChart 
            data={genre_analysis} 
            title="Top 15 Genres" 
            x="genre_name" 
            y="count"
            legend=false
            swapXY=true
          />
        </Grid>
    </Tab>
    
    <Tab label="Genre Trends">
        <BarChart 
          data={yearly_genre_breakdown} 
          title="Genre Distribution by Year" 
          x="genre_name" 
          y="count" 
          series="genre_name"
          legend=true
        />
    </Tab>
    
    <Tab label="Movies Data">
        <DataTable 
          data={movies_table}
          search=true
          rows=20
        />
    </Tab>
</Tabs>

### Key Insights

The data shows <Value data={total_movies} column=total_count /> movies scheduled for release from 2025 onwards. This represents the future pipeline of the film industry and emerging genre trends.

**Genre Analysis:**
- The most popular genre is <Value data={genre_analysis} column=genre_name row=0 />
- Top genres reflect current market preferences and industry focus

**Release Patterns:**
- Movies are distributed across multiple years starting from 2025
- The data provides insights into long-term industry planning and production schedules