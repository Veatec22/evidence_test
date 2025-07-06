---
title: GitHub Data
queries:
  - recommendations.sql
  - starred.sql
---

```sql recommendations
SELECT
    name,
    stars,
    language,
    url,
FROM github.recommendations
ORDER BY stars DESC
```

```sql stack_count
SELECT COUNT(*) AS stack_count
FROM github.starred
WHERE all_tags LIKE '%stack%'
```

```sql recommendations_count
SELECT COUNT(*) AS recommendations_count
FROM github.recommendations
```

```sql stack_barchart
SELECT 
    COUNT(*) AS stack_count,
    categories
FROM github.starred
WHERE all_tags LIKE '%stack%'
GROUP BY ALL
```

```sql backlog_barchart
SELECT 
    COUNT(*) AS backlog_count,
    categories
FROM github.starred
WHERE all_tags LIKE '%future-ideas%'
GROUP BY ALL
```

```sql unique_categories
SELECT
    categories
FROM github.starred
GROUP BY 1
```

```sql unique_curated_tags
SELECT
    curated_tags
FROM github.starred
GROUP BY 1
```

```sql starred
SELECT 
    name,
    stars,
    language,
    url,
    last_release,
    curated_tags,
    categories,
    all_tags,
    is_curated,
FROM github.starred
WHERE categories LIKE '${inputs.selected_category.value}'
AND curated_tags LIKE '${inputs.selected_curated_tag.value}'
ORDER BY stars DESC
```

This pages serves several purposes:
- a small portfolio project with a usage of [Evidence](https://evidence.dev/).
- a hub for my stack and recommended repositories.

<Grid cols=2>
    <BigValue 
        data={stack_count} 
        value=stack_count
        title="Portfolio Size"
        description="Total repositories marked as stack" 
    />
    <BigValue 
        data={recommendations_count} 
        value=recommendations_count
        title="Total Recommendations"
        description="Repositories with similar topics and +1000 stars that are not starred" 
    />
</Grid>

<Grid cols=2>
    <BarChart 
        data={stack_barchart} 
        title="Stack Divided by Categories" 
        x="categories" 
        y="stack_count"
        swapXY=true
        series="categories"
    />
    <BarChart 
        data={backlog_barchart} 
        title="Backlog Divided by Categories" 
        x="categories" 
        y="backlog_count"
        swapXY=true
        series="categories"
    />
</Grid>


<Tabs fullWidth=true>
    <Tab label="Starred">
        <Dropdown
            name=selected_category
            data={unique_categories}
            value=categories
        >
            <DropdownOption value="%" valueLabel="All Categories"/>
        </Dropdown>
        <Dropdown
            name=selected_curated_tag
            data={unique_curated_tags}
            value=curated_tags
        >
            <DropdownOption value="%" valueLabel="All Curated Tags"/>
        </Dropdown>
            <DataTable
        data={starred}
        search=true
        rows=10
    >
        <Column id=name />
        <Column id=stars />
        <Column id=language />
        <Column id=url contentType=link linkLabel=name />
        <Column id=url contentType=link linkLabel=name />
    </DataTable>
    </Tab>
    <Tab label="Recommendations">
          <DataTable
            data={recommendations}
            search=true
            rows=10
        >
        <Column id=name />
        <Column id=stars />
        <Column id=language />
        <Column id=url contentType=link linkLabel=name />
    </DataTable>
    </Tab>
</Tabs>