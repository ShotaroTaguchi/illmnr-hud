# 開発メモ

## 仕組み

1つのデザイン（`illmnr/design.py`）を、出力先ごとのビルドスクリプトでファイルに書き出す。
Dash Studio や RBRHUD のエディタで手作業で組まない。

```
illmnr/                    # 共通パッケージ
├── design.py              # デザインの本体：配色、PREFIX/AUTHOR、Engine パネルの寸法、シフトライト
├── simhubdash.py          # SimHub 用部品：rect / text / ellipse / vbar / hbar / layer、formula / gradient、zip 出力
├── rbr.py                 # SimHub × RBR：NGP のプロパティ名、build()
└── rbrhud.py              # RBRHUD 用：Element（アトラス生成・数字フォント埋め込み・.element 出力）
simhub/<game>/build_*.py   # SimHub 版（1ファイル = 1オーバーレイ。Time/Delta だけ1ファイルで2つ）
rbrhud/build_*.py          # RBRHUD 版
dist/                      # 生成物。公開用にコミットする
├── simhub/<game>/ILLMNR_<GAME>_<Name>.simhubdash
└── rbrhud/OverlayElements/{Custom,textures}/ILLMNR_<Name>.*
build.py                   # 全部ビルド ＋ RBRHUD の配布用 zip（dist/rbrhud/ILLMNR-HUD_RBRHUD.zip）
docs/make_logo.py          # README のロゴ（design の色から生成）
```

```
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # 初回のみ（RBRHUD に Pillow が必要）
.venv/Scripts/python build.py                                           # 全部
.venv/Scripts/python simhub/rbr/build_engine.py                         # 個別
```

- 名前はすべて `illmnr.design.PREFIX`（`ILLMNR`）で始める。ほかの人の配布物と混ざらないように
- 生成は決定的（zip の時刻固定・UUID は名前から生成）。中身が変わらなければ同じファイルになる
- 構成を変えたときは、生成物のチェックサムが変わらないことで確認できる

## SimHub

### 新しいオーバーレイ・ゲームを足す

1. `simhub/<game>/build_<name>.py` を作る（既存を雛形に。ゲーム固有のプロパティ名は `illmnr/<game>.py` に）
2. 値は SimHub のプロパティ式（NCalc）で書く。例：`[DataCorePlugin.GameData.NewData.Gear]`
3. 色を値で変えるときは `gradient()`（2〜3色の補間）、回転は `rect(..., rotation=式)`（自身の中心で回る）
4. レイアウトは1倍で書き、既定サイズは `build(..., sx=, sy=)` の倍率で決める（文字・角丸・線幅は小さいほうの倍率）
5. ビルド → 取り込み → 実走で確認 → README に追記

### 注意

- `.djson` は Newtonsoft JSON（`$id` / `$values`）。`simhubdash.py` が自動で付ける
- フィールド構成は SimHub 9.13 の書き出しに合わせている。読めなくなったら Dash Studio で保存したファイルと見比べる
- ハンドルのスポークやマークは「中心を揃えた四角の、片側の枠線だけ描く」ことで、回転の中心をハンドル中心に合わせている
- 四角の `Width` を式で動かしても SimHub 9.13 では反映されなかった。伸び縮みするバーはゲージ（`vbar` / `hbar`）で作る
  - `hbar(from_right=True)` で右から左へ伸びる（Delta の赤いバー）

## RBRHUD

RSF 同梱の RBRHUD プラグイン（`<RBR>/Plugins/RBRHUD/`）のエレメントを生成する。ゲーム内に描画するのでリプレイでも動く。

```
OverlayElements/
├── textures/<Atlas>.png + .ini   # アトラス：部品画像1枚 + 「名前=x,y,幅,高さ」。フォントもここに入る
└── Custom/*.element              # エレメント（ini 形式）：[main] + 部品ごとのセクション
Overlays/*.ini                    # どのエレメントをどこに出すか（走行用・リプレイ用。rbrhud.ini で選択）
```

### 分かったこと（作ってみて）

- **アトラスは縦横とも2の累乗**（1024×512 など）。半端なサイズだと切り出しがずれて崩れる
- **フォントはアトラスの中のビットマップ**。`[フォント名]` セクションに `charset=x,y,幅,高さ`（アトラス内の範囲）と `文字コード=x,y,幅,高さ`（範囲内の位置）。
  1エレメントは1アトラスしか使えないので、`Bahnschrift` など同梱フォントは自分のアトラスに無いと使えない（「Failed to create drawable number object」）。
  → `build_engine.py` が Segoe UI で数字フォントを描いて埋め込む（大きさも SimHub 版と一致する）
- 部品の種類：`Static`（固定画像）、`Simple`（条件で表示：`equal = n`、`rangemin / rangemax`）、`Number`（`font` / `format` / `justification`）、
  `Expanding`、`Rotating`、`Colour`（`value0..2 / colour0..2`）、`Pie`
- 効果は `type = Effect` のセクションで定義して部品の `effect =` で参照：`Blink|`、`ColourChange|`、`Show|`、`Hide|`、`Pulse|`（`data` が真のとき）
- 色は `aarrggbb`（小文字・`#` なし）。白で描いた画像に `colour` で色を付けられる
- `Number` の `justification = Right` は `xpos` が右端
- データ名（DLL から抽出）：`RPM`、`RPMPercent`、`UpShift`、`Gear`（0=R, 1=N, 2=1速…）、`SpeedKPH`、`RaceTime`、`DeltaTime`、
  `CoolantTemperatureC`、`RadiatorCoolantTemperatureC`、`OilTemperatureC`、`*Warning`、`Input*Processed`、`InputSteeringDeg`、
  `TireHealth{LF,RF,LR,RR}{Avg,Worst}`、`Damage*`、`DistanceDriven*`、`DistanceToFinish*`、`RSF.*` など。**タイヤ温度・空気圧は無い**

### 新しいエレメントを足す

`illmnr.rbrhud.Element` で、SimHub 版と同じ1倍レイアウトから作る（`rbrhud/build_*.py` が例）。

- `Rotating` は中心座標で置く（既存の InputDisplay から推定）。Inputs のハンドルは `InputSteeringDeg` を 1:1 で回す
- `Expanding` は `expandmap0/1value → expand` の対応で伸びる。`direction` は up / down / left / right
- 効果の条件：`ColourChange` / `Blink` は `threshold` を超えたとき、`Show` は `limit` 未満、`Hide` は `threshold` を超えたとき
- Number の `format`：Whole、Decimal1/2、Percentage、TimeMinSec、TimeMinSecM/Ms/Msc、TimeSeconds、Padded3/4

## 調整用の定数

| ファイル | 定数 | 内容 | 既定 |
|---|---|---|---|
| `illmnr/design.py` | 色、`PREFIX`、`AUTHOR` | 全出力先共通 | |
| | `SHIFT_LIGHTS` | シフトライトの点灯％と色（SimHub / RBRHUD 共通） | 55〜95% |
| | `ENGINE_W / H / SIDE` | Engine パネルの1倍レイアウト | 400 / 114 / 12 |
| `simhub/rbr/build_engine.py` | `SCALE_X / SCALE_Y` | 既定サイズの倍率 | 1.5 / 1.6 |
| | `WATER_OK / WATER_HOT` | 水温の文字色：白になる温度 / 赤になる温度（℃。OK−30℃で青） | 90 / 110 |
| | `OIL_OK / OIL_HOT` | 油温の文字色（同上） | 110 / 130 |
| `simhub/rbr/build_tyres.py` | `SCALE` | 既定サイズの倍率 | 0.75 |
| | `TYRE_COLD / OK / HOT` | タイヤ色の境目（℃） | 40 / 70 / 100 |
| `simhub/rbr/build_inputs.py` | `STEER_LOCK_DEG` | ハンドル表示の回転角（ロック to ロック） | 540 |
| | `STEER_SIGN` | 回転方向（逆なら -1） | 1 |
| `simhub/rbr/build_time.py` | `SCALE` | Time / Delta の既定サイズの倍率 | 1.2 |
| | `DELTA_RANGE` | Delta の数字が完全な緑／赤になる差（秒） | 1.0 |
| | `DELTA_BAR_RANGE` | Delta のバーが端まで伸びる差（秒、比例） | 10.0 |
| `simhub/rbr/build_brakes.py` | `BRAKE_COLD / OK / HOT` | ブレーキ色の境目（℃。仮の値） | 150 / 350 / 650 |
| `rbrhud/build_*.py` | `S` | 1倍レイアウトに掛ける倍率（SimHub 版と同じ大きさ） | Engine 1.5、Time/Delta 1.2、Inputs 1.0 |
| `rbrhud/build_time.py` | `DELTA_BAR_RANGE` | Delta のバーが端まで伸びる差（秒） | 10.0 |

## RBR（NGP）のプロパティ（SimHub）

NGP は 664 バイトの UDP パケットを送り、SimHub では全項目が `GameRawData.NGPTelemetry.<パス>` で読める。
構造の定義元：[mika-n/RBRUDPTelemetryLogger](https://github.com/mika-n/RBRUDPTelemetryLogger)（`TelemetryData.h`）。
**リプレイ中は送られない**（実機で確認）。

| 項目 | パス | 単位 |
|---|---|---|
| ギア | `control.gear` | 0=R, 1=N, 2=1速… |
| 操作入力 | `control.steering / throttle / brake / handbrake / clutch` | 0〜1（ステア -1〜1） |
| 速度・回転数 | `car.speed`、`car.engine.rpm` | km/h、rpm |
| 水温 / ラジエーター水温 / 油温 | `car.engine.engineCoolantTemperature / radiatorCoolantTemperature / engineTemperature` | K |
| 姿勢・G | `car.roll / pitch / yaw`、`car.accelerations.surge / sway / heave` | |
| ステージ | `stage.progress / raceTime / distanceToEnd` | m / 秒 / m |

4輪は `car.suspensionLF / RF / LB / RB` の下（LB/RB が後輪）

| 項目 | パス | 単位 |
|---|---|---|
| ストローク | `springDeflection` | |
| ダンパー | `damper.damage / pistonVelocity` | |
| ブレーキ | `wheel.brakeDisk.temperature / wear` | K |
| タイヤ | `wheel.tire.pressure`、`treadTemperature / carcassTemperature / temperature` | Pa、K |
| タイヤ摩耗 | `wheel.tire.segment1〜8.wear`（8区画の使用量） | 0〜1 |

- 温度はケルビン（`- 273.15` で℃）。`engineTemperature` は車両メーターの Oil T と一致したので油温として扱う
- 実走で確認済み：ギア、速度、回転数、エンジン温度、タイヤ温度・空気圧・摩耗。その他は未確認

SimHub 標準プロパティ（`DataCorePlugin.GameData.NewData.` 以下、RBR で動作確認済み）：
`Gear`、`SpeedKmh`、`Rpms`、`CarSettings_CurrentDisplayedRPMPercent`（車ごとのレッドライン基準の％）、`CarSettings_RPMRedLineReached`

## デザインの経緯（決めたことと、やめた案）

照太郎が実機で見て決めたこと。理由ごと残しておく。

- **パネルは真っ黒・不透明**（`#FF000000`）。半透明（69%→92%）は車両のメーターが透けて読みにくく、青みがかった黒（`#101418`）より真っ黒が好み
- **Engine は横長**：中央に大きなギア、右に速度と回転数、左に温度3つを左右対称に。最初の縦長はやめた
- **温度のラベル**：`ENGINE` は何の温度か分からない → 車両メーターの Oil T と一致したので `OIL`。`RADIATOR` → `RAD WATER`。
  油温は水温と別の色の基準（110 / 130℃）。水温の基準のままだと普通の油温でも赤くなった
- **Tyres は1輪1タイル**：参考にした既存オーバーレイの上下分割は分かりにくくカクカクしていたのでやめた。背景色をなめらかに変える。
  タイルはやや縦長（84×100）、摩耗バーは外側（左のタイヤは左端、右は右端）。内側だと隣のタイルのバーに見えた
- **Delta のバー**：比例で 10 秒で端まで（照太郎の指定）。平方根のカーブ（小さい差で大きく伸びる）は提案したが不採用。数字の色は 1 秒で完全な緑／赤
- **既定サイズ**：Engine 1.5×1.6、Tyres 0.75、Inputs 1.0、Time/Delta/Stage 1.2（照太郎の指定。数字はざっくりでよいと言われている）
- **ロゴ**：シフトライト10色＋「ILLMNR」白・「-HUD」グレー、下に「heads-up display for sim racing · by illuminer」
- ATOM 側（boards-sandbox）の LED は緑・黄・橙・赤、シフトポイントで赤点滅（青点滅は不採用）

## 照太郎の実機環境（2026-11 時点）

- 画面 1920×1080。Windows、Python 3.12.10、SimHub 9.13.2、RSF Installation V1.59.3、MOZA Pit House 1.4.1.13（R5 ＋ ES ステアリング）
- SimHub のレイアウト `RBR-Telemetry`（左上の座標と大きさ, px）：
  Time (1,4) 240×98 / Delta (1,101) 240×98 / Stage (2,982) 240×98 / Engine (647,887) 624×208 /
  Inputs (1302,930) 310×150 / Brakes (1763,789) 156×123 / Tyres (1763,912) 156×168
  → タイム系は左上、Engine は下中央、Inputs とタイヤ系は右下。サイズを変えるときは周りとの兼ね合いに注意
  （座標と大きさは SimHub の枠のもの。枠には透明な余白 `PAD`×倍率 が含まれるので、見えるパネルはひと回り小さい。
  Engine の枠は画面下から約15px出るが、出るのはほぼ余白だけ。Brakes と Tyres は枠が接しているが、パネルの間には約12pxのすき間がある）
- RBRHUD はリプレイ用オーバーレイ（`Replay_ShowInfo_Simple.ini`）に配置：Time・Delta は左上、Engine（倍率 0.75 に縮小）と Inputs は下中央

## 仮の値・確認状況

- Brakes の色の境目（150 / 350 / 650℃）は**根拠のない仮の値**（実データを見ていない）。摩耗の向き（0＝新品）も未確認。
  SimHub 上で「表示されること」は確認済み
- RBRHUD の Time・Delta・Engine・Inputs はリプレイ中の表示を確認済み（Delta は 0.00 の状態のみ。差が付いたときの色とバーの向きは未確認）。
  Inputs のハンドルが上の縁に当たっていたのは修正済みだが、修正後の表示は未確認
- サスペンション（`springDeflection`）と G（`accelerations`）は**実データを一度も見ていない**（範囲・単位・符号の向きは不明）
- 次に作るゲームはまだ決めていない（プロパティの調査も未着手）。リリースは v0.1.0 のみ

## メンテナンスのメモ

- **寸法は `illmnr/design.py` に1か所だけ**（パネルの左上が基準）。SimHub は `PAD` を足し、RBRHUD はそのまま使う。
  出力先ごとに数値を書き写すとずれる（RBRHUD の Inputs でハンドルが上の縁に当たったのは、`PAD` を引き忘れたため）
- 構成だけを変える変更は、ビルド前後で `dist/` のチェックサムが変わらないことを確かめる（生成は決定的）
- ロゴは `docs/make_logo.py` で生成（design の色から）。ロゴも RBRHUD のテクスチャも Windows のフォント（Bahnschrift、Segoe UI）を使うので、Windows でビルドする
- README の画面写真（`docs/images/rbr-overlays.png`、`rbrhud-replay.png`）は実機のスクリーンショット。見た目を変えたら撮り直す
- **名前を変えると、置いた位置が外れる**：SimHub はレイアウト（`OverlayLayouts/*.olayout`）が `DashTemplates\<名前>\<名前>.djson` で、
  RBRHUD はオーバーレイ（`Plugins/RBRHUD/Overlays/*.ini`）が `Custom/<名前>.element` で参照している。改名するときはこの参照も書き換える
- リリース：`build.py` → コミット → `gh release create vX.Y.Z dist/rbrhud/ILLMNR-HUD_RBRHUD.zip dist/simhub/rbr/*.simhubdash`
- コミットのメールは GitHub の匿名アドレス（このリポジトリと PC 全体の git 設定で指定済み）

## TODO

- 実機で確認：RBRHUD の Delta（差が付いたときの色とバーの向き）と Inputs（修正後の位置）、SimHub の Brakes（温度の範囲、摩耗の向き）
- 候補：サスペンションのストローク、G（単位と向きを実データで確かめてから）
- ほかのゲームの SimHub 版（`simhub/<game>/`）
