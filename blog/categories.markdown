---
layout: page
title: カテゴリ
permalink: /categories/
---

<p class="taxonomy-intro">カテゴリごとに記事を一覧できます。</p>

{%- assign sorted_categories = site.categories | sort -%}

<div class="taxonomy-groups">
{%- for category in sorted_categories -%}
  {%- assign category_name = category | first -%}
  {%- assign posts = category | last -%}

<section class="taxonomy-group" id="{{ category_name | slugify }}">
  <div class="taxonomy-heading">
    <h2>{{ category_name }}</h2>
    <p>{{ posts.size }} 件</p>
  </div>
  <ul class="taxonomy-list">
  {%- for post in posts -%}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
      <span>{{ post.date | date: "%Y-%m-%d" }}</span>
    </li>
  {%- endfor -%}
  </ul>
</section>
{%- endfor -%}
</div>
