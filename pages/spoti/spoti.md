---
title: spoti
description: test from bq
queries:
  - spoti.sql
---

```sql avg_all
SELECT AVG(acousticness) as avg_acousticness, AVG(danceability) as avg_danceability, AVG(energy) as avg_energy, AVG(instrumentalness) as avg_instrumentalness, AVG(liveness) as avg_liveness, AVG(speechiness) as avg_speechiness, AVG(valence) as avg_valence, AVG(tempo) as avg_tempo
FROM spoti
```

```sql spoti_barchart_genre
SELECT playlist_genre,playlist_subgenre, COUNT(*) as count_genres
FROM spoti
GROUP BY ALL
```

```sql spoti_donut_data
SELECT mode as name, COUNT(*) as value
FROM spoti
GROUP BY mode
```

```sql spoti_table
SELECT *
FROM spoti
```

    <BigValue  data = {avg_all} value = avg_acousticness description="test"/>
    <BigValue  data = {avg_all} value = avg_danceability />
    <BigValue  data = {avg_all} value = avg_energy />
    <BigValue  data = {avg_all} value = avg_instrumentalness />
    <BigValue  data = {avg_all} value = avg_liveness />
    <BigValue  data = {avg_all} value = avg_speechiness />
    <BigValue  data = {avg_all} value = avg_valence />
    <BigValue  data = {avg_all} value = avg_tempo />

### test_subtitle
As you can see, you could easily addtext and explain to user what he can see.

<Tabs fullWidth=true>
    <Tab label="Charts">
        <Grid cols=2>
          <BarChart 
          data={spoti_barchart_genre} 
          title="count_genres" 
          x="playlist_genre" 
          y="count_genres" 
          series="playlist_subgenre"
          legend=false
          echartsOptions={
                  {
                      tooltip: {
                          show: false
                      }
                  }
                }
          />

          <ECharts config={
              {
                title: {
                  text: 'Mode Distribution',
                  left: 'center',
                  top: 'bottom'
                },
                tooltip: {
                      formatter: '{b}: {c} ({d}%)'
                  },
                series: [
                  {
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: [...spoti_donut_data],
                  }
                ]
                }
              }
          />
        </Grid>
    </Tab>
    <Tab label="Table">
        <DataTable data={spoti_table}/>
    </Tab>
</Tabs>

The number of total tracks is <Value data = {spoti_barchart_genre} column = count_genres agg = sum />.




