# ILLMNR-HUD の背景

照太郎（GitHub: ShotaroTaguchi、ゲーム内の表示名 illuminer）と Claude で作っている、自分用の HUD デザイン集。
最初は RBR（Richard Burns Rally / RallySimFans 版）の SimHub オーバーレイとして始まり、
「デザインが気に入ったので、ほかのゲームでも同じ見た目で使いたい」「リプレイでも出したい」となって、
1つのデザインを SimHub と RBRHUD の両方に書き出す形になった。いずれ公開するかもしれない（今は Private）。

詳しい構成・調整用の定数・分かったことは `docs/development.md`、使う人向けは `README.md` にある。

## これまでの進め方

- 照太郎が実機（RBR + SimHub、MOZA R5 / ES ステアリング）で表示を見て、スクリーンショットや動画で感想をくれる → 直す、の繰り返し。
  見た目の好みはかなりはっきりしているので、迷ったら案を見せて選んでもらうと早い
- やり取りは日本語。ゲームやシムレースには詳しい
- 動作確認はローカル（RBR・SimHub が入った Windows PC）でしかできない。Web からの作業ならコードとドキュメントまで
- コミットメッセージは `feat: ...` / `fix: ...` / `docs: ...` のような小文字の形にしてきた。生成物（`dist/`）もコミットしている（ダウンロードしてすぐ使えるように）

## ハマったこと（事実として）

- SimHub：四角の `Width` を式で動かしても反映されなかった → バーはゲージで作っている
- RBRHUD：アトラス画像は縦横2の累乗でないと崩れる。フォントはアトラス内のビットマップで、1エレメント1アトラスなので自前で埋め込んでいる
- RBR：NGP の UDP テレメトリはリプレイ中に出ない。RBRHUD はリプレイでも動く
- RBR：`RichardBurnsRally.ini` の UDP 送り先は、カンマの後に空白が入ると2つ目以降に届かなくなる（MOZA Pit House が書き換えたときに起きた）

## 関連する場所

- `C:\GitRepos\05_sim_racing\sim-racing` … 走りやトラブル対応のメモ（`i_made/RBR_TroubleShooting.md`）
- `C:\GitRepos\04_boards\boards-sandbox\rbr-telemetry` … 同じ UDP を受けて回転数を光らせる M5Stack ATOM Matrix
- RBR 本体は `D:\Richard Burns Rally`、RBRHUD は `Plugins\RBRHUD\`
