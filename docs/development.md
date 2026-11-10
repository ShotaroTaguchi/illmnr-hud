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
build.py                   # 全部ビルド
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

## TODO

- 実機で確認：RBRHUD の Inputs / Time / Delta（位置の基準、伸びる向き、書式）、SimHub の Brakes（温度の範囲、摩耗の向き）と Stage
- 候補：サスペンションのストローク、G（単位と向きを実データで確かめてから）
- ほかのゲームの SimHub 版（`simhub/<game>/`）
