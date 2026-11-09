# 開発メモ

## 仕組み

Dash Studio で手作業で組まず、Python で SimHub のダッシュボードファイル（`.djson`）を生成している。

```
tools/
├── simhubdash.py          # 共通部品：rect / text / ellipse / vbar / layer、formula / gradient、zip 出力
├── rbr_common.py          # RBR 用の配色・プロパティ名・build()
└── build_rbr_<name>.py    # オーバーレイ定義（1ファイル = 1オーバーレイ）
dist/                      # 生成物。公開用にコミットする
```

```
python tools/build_rbr_engine.py    # -> dist/RBR_Engine.simhubdash
python tools/build_rbr_tyres.py     # -> dist/RBR_Tyres.simhubdash
python tools/build_rbr_inputs.py    # -> dist/RBR_Inputs.simhubdash
python tools/build_rbr_time.py      # -> dist/RBR_Time.simhubdash, dist/RBR_Delta.simhubdash
```

Python 3.10+、標準ライブラリのみ。同名のダッシュボードを取り込むと上書きされる（SimHub が旧版をバックアップする）。

### 新しいオーバーレイを足す

1. `tools/build_<name>.py` を作る（既存の `build_rbr_*.py` を雛形に）
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
- `.simhubdash` の zip は時刻を固定して書き出すので、中身が変わらなければ同じファイルになる

## RBR オーバーレイの調整用定数

| ファイル | 定数 | 内容 | 既定 |
|---|---|---|---|
| `build_rbr_engine.py` | `SCALE_X / SCALE_Y` | 既定サイズの倍率（レイアウトは1倍で記述） | 1.5 / 1.6 |
| | `SHIFT_LIGHTS` | シフトライトの点灯％と色 | 55〜95% |
| | `WATER_OK / WATER_HOT` | 水温の文字色：白になる温度 / 赤になる温度（℃。OK−30℃で青） | 90 / 110 |
| | `OIL_OK / OIL_HOT` | 油温の文字色（同上） | 110 / 130 |
| `build_rbr_tyres.py` | `SCALE` | 既定サイズの倍率 | 0.75 |
| | `TYRE_COLD / OK / HOT` | タイヤ色の境目（℃） | 40 / 70 / 100 |
| `build_rbr_inputs.py` | `STEER_LOCK_DEG` | ハンドル表示の回転角（ロック to ロック） | 540 |
| | `STEER_SIGN` | 回転方向（逆なら -1） | 1 |
| `build_rbr_time.py` | `SCALE` | Time / Delta の既定サイズの倍率 | 1.2 |
| | `DELTA_RANGE` | Delta の数字が完全な緑／赤になる差（秒） | 1.0 |
| | `DELTA_BAR_RANGE` | Delta のバーが端まで伸びる差（秒、比例） | 10.0 |
| `rbr_common.py` | 色定数・`AUTHOR` | 全オーバーレイ共通 | |

### RBR（NGP）のプロパティ

NGP は 664 バイトの UDP パケットを送り、SimHub では全項目が `GameRawData.NGPTelemetry.<パス>` で読める。
構造の定義元：[mika-n/RBRUDPTelemetryLogger](https://github.com/mika-n/RBRUDPTelemetryLogger)（`TelemetryData.h`）

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

- オーバーレイ名が `RBR_*` だと、ほかの人が配布している RBR 用ダッシュボードと SimHub 上で混ざる。固有の接頭辞を付けて改名する（ファイル名・タイトル・README を合わせて変更）
