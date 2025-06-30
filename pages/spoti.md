---
title: spoti
description: test from bq
queries:
  - spoti.sql
---

```sql spoti_sample
SELECT playlist_genre, AVG(speechiness) as avg_speechiness
FROM spoti
GROUP BY playlist_genre
```


<BarChart data={spoti_sample} title="avg_speechiness" x="playlist_genre" y="avg_speechiness" />

