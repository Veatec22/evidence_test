---
title: IMDB Movies 2025+
description: Analysis of IMDB movie data from 2025 onwards
queries:
  - imdb.sql
---

```sql total_movies
SELECT COUNT(*) as total_count
FROM imdb
```

```sql movies_by_year
SELECT start_year, COUNT(*) as movie_count
FROM imdb
GROUP BY start_year
ORDER BY start_year
```

```sql genre_analysis
SELECT 
  TRIM(genre) as genre_name,
  COUNT(*) as count
FROM imdb,
UNNEST(SPLIT(genres, ',')) as genre
WHERE genre IS NOT NULL AND TRIM(genre) != ''
GROUP BY genre_name
ORDER BY count DESC
LIMIT 15
```

```sql movies_table
SELECT primary_title, start_year, genres
FROM imdb
ORDER BY start_year DESC, primary_title
LIMIT 100
```

```sql yearly_genre_breakdown
SELECT 
  start_year,
  TRIM(genre) as genre_name,
  COUNT(*) as count
FROM imdb,
UNNEST(SPLIT(genres, ',')) as genre
WHERE genre IS NOT NULL AND TRIM(genre) != ''
GROUP BY start_year, genre_name
ORDER BY start_year, count DESC
```

<BigValue data={total_movies} value=total_count description="Total Movies from 2025+" />

## Movie Industry Analysis (2025+)

This analysis examines upcoming and recently released movies from 2025 onwards, providing insights into genre trends and release patterns in the modern film industry.

<Tabs fullWidth=true>
    <Tab label="Overview Charts">
        <Grid cols=2>
          <BarChart 
            data={movies_by_year} 
            title="Movies by Release Year" 
            x="start_year" 
            y="movie_count"
            legend=false
          />

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
          x="start_year" 
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