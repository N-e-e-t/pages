---
layout: page
title: Categories
permalink: /categories/
---

{%- assign sorted_categories = site.categories | sort -%}

{%- for category in sorted_categories -%}
  {%- assign category_name = category | first -%}
  {%- assign posts = category | last -%}

## <span id="{{ category_name | slugify }}">{{ category_name }}</span>

{%- for post in posts -%}
- [{{ post.title | escape }}]({{ post.url | relative_url }}) - {{ post.date | date: "%Y-%m-%d" }}
{%- endfor -%}

{%- endfor -%}
