# N-e-e-t Lab

公開サイト: https://n-e-e-t.github.io/pages/

トップページはルートのHTML、ブログは `blog/` のJekyllで管理しています。`.github/workflows/deploy.yml` が両方を `_site/` にまとめて公開します。

## 検索向け設定

- `blog/_config.yml`: Jekyll SEO Tag、Jekyll Sitemap、日本語・日本時間の設定。
- `blog/_includes/seo.html`: canonical、description、OGP、記事のJSON-LD。タイトルは既存のレイアウトで出力します。
- 記事のfront matterに `description` を書くと、メタ情報とブログ一覧の要約に使われます。
- 公開済み記事の `permalink` は維持してください。カテゴリやタイムゾーンの変更でURLを変えないための設定です。
- トップページの「ブログから」は手動で選んだ記事へのリンクです。紹介記事を変える場合は `index.html` を編集します。
- `images/home.webp` はトップ背景用の軽量版、`images/home.png` は元画像です。

## サイトマップ

Search Consoleに送信するURL:

```text
https://n-e-e-t.github.io/pages/sitemap.xml
```

このインデックスから、固定ページの `site-pages.xml` とブログが自動生成する `blog/sitemap.xml` を参照します。ブログの記事追加は自動反映されます。ルートに固定ページを追加する場合は `site-pages.xml` にも追加してください。404ページは対象外です。

`/pages/robots.txt` や `/pages/blog/robots.txt` はドメイン全体のクロール制御には使えません。ドメイン直下の `https://n-e-e-t.github.io/robots.txt` はこのリポジトリとは別に管理されています。

## 生成物の検証

GitHub ActionsはJekyll生成後、公開前に次を実行します。

```text
python3 checks/check_site.py _site
```

Windowsで生成済みのサイトを確認する場合:

```text
uv run python checks/check_site.py <生成先のディレクトリ>
```

チェック内容は、タイトル・description・canonicalの重複、記事のJSON-LD、内部リンクとアンカー、サイトマップ内URL、404除外、学マス記事の既存URL・公開日時です。Python標準ライブラリのみで動作します。
