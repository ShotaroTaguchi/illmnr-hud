# RBRHUD 版の方向性（未着手）

SimHub のオーバーレイは NGP の UDP テレメトリで動くため、**リプレイ中は止まる**（NGP がリプレイ中に送信しない。実機で確認）。
リプレイでも同じデザインで表示したいので、ゲーム内に描画する RBRHUD（RSF 同梱プラグイン）で同じ見た目を作る。

## RBRHUD の仕組み（`D:\Richard Burns Rally\Plugins\RBRHUD\` を読んだ範囲）

```
OverlayElements/
├── textures/<Atlas>.png + <Atlas>.ini   # 部品画像を1枚にまとめたアトラス。ini に 名前=x,y,幅,高さ
├── Default/*.element, RallyClean/*.element ...  # 表示部品（ini 形式）
└── Custom/                              # 自作エレメントの置き場所
Overlays/*.ini                           # どのエレメントをどこに出すか（走行用・リプレイ用で別ファイルあり）
```

`.element` は `[main]`（atlas / description など）＋ 部品ごとのセクション。部品の種類：

| type | 用途 | 例 |
|---|---|---|
| `Static` | 固定画像 | 背景パネル |
| `Expanding` | 値で伸びる画像（`direction = up` など） | ペダルバー、シフトライト |
| `Rotating` | 値で回る画像 | ハンドル |
| `Number` | 数値（`font` / `format` = Whole, Decimal1, Percentage, TimeMinSecM） | 速度、タイム |
| `Colour` | 値で色を変える | 温度の色分け |
| `Simple` / `Effect` / `Damage` / `Pie` | その他 | |

既存エレメントで使われているデータ名（全量ではない）：
`RPM`, `RPMPercent`, `EngineRPMLimit`, `UpShift`, `Gear`, `SpeedKPH`, `RaceTime`, `DeltaTime`, `DeltaGain`,
`InputSteeringDeg`, `InputSteeringProcessed`, `InputThrottleProcessed`, `InputBrakeProcessed`, `InputClutchProcessed`, `InputHandbrakeProcessed`,
`CoolantTemperatureC`, `OilTemperatureWarning`, `OilPressurePsi`, `TurboPressureBar`,
`TireHealthLFAvg` ほか4輪, `DistanceDrivenPercent`, `DistanceToFinish`, `RSF.StageName`, `RSF.CarName` …

フォント：`Bahnschrift`, `font_arial`, `FontDigital7`, `Prototype`, `WRC_Clean` など同梱のもの。

## 進め方

1. **アトラスを生成する**：`tools/` に Python（Pillow）で、黒い角丸パネル・バーの塗り・ハンドル（リム＋スポーク＋オレンジのマーク）・LED を描いた PNG と、切り出し位置の ini を出力する
2. **エレメントを生成する**：SimHub 版と同じレイアウト定義から `.element` を書き出す（Inputs → Engine → Time/Delta の順。Inputs は既存の `Default/InputDisplay.element` が雛形になる）
3. **配置**：`OverlayElements/Custom/` と `textures/` にコピー、`Overlays/` に走行用・リプレイ用の配置を作る（既存の `Replay_*.ini` を参考に）
4. ゲーム内の RBRHUD エディタで位置を微調整し、保存された値をコードに戻す

## 先に確かめること

- **リプレイで各データが動くか**（`Digidash_ReplayBig.element` や `Replay_*.ini` があるので、回転数・入力は動く見込み）
- **タイヤ温度があるか**：既存エレメントには `TireHealth*`（摩耗）しか見当たらない。温度・空気圧は無いかもしれない
- データ名の全一覧（RBRHUD のゲーム内エディタで選べる候補を確認する）
- `Colour` の書式（温度で色を変える）、`Rotating` の回転角の指定（`InputDisplay.element` は `rotation0deg / rotation0value` で対応付け）
- アトラスの画像サイズ・形式の制約（既存は PNG。DDS が必要な場面があるか）
