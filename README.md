# wakapanda.com — 和歌ぱんだ公式サイト

パンダ映像チャンネル「和歌ぱんだ」のハブサイト。GitHub Pagesで公開する静的サイトです。

## 構成

```
index.html            トップページ
about.html            このサイトについて(運営者情報)
policy.html           運営ポリシー(広告表記・プライバシー・免責)
css/style.css         デザイン
js/main.js            動画・ニュース一覧の描画
data/videos.json      最新動画リスト(毎日自動更新・手で編集しない)
data/news.json        パンダNOWの記事(ここに追記して更新する)
scripts/update_videos.py          videos.json を作るスクリプト
.github/workflows/update-videos.yml  毎朝6時ごろに自動実行
CNAME                 独自ドメイン設定(wakapanda.com)
```

## 更新のしかた

- **最新動画**: 何もしなくてOK。毎朝自動でYouTubeから反映されます
- **パンダNOW**: `data/news.json` に新しい記事を先頭に追記してコミット
- **それ以外の文章**: 各HTMLを直接編集

## 公開設定(初回のみ)

1. GitHubリポジトリの Settings → Pages → Branch を `main` / `(root)` にして保存
2. Settings → Pages → Custom domain に `wakapanda.com` を入力し、「Enforce HTTPS」にチェック
3. お名前.comのDNS設定は `Desktop/secretary/wakapanda/サイト公開手順.md` を参照
