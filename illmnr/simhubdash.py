"""Minimal builder for SimHub dashboard files (.djson / .simhubdash).

SimHub stores dashboards as Newtonsoft JSON with $id / $values wrappers.
The field sets below were copied from dashboards exported by SimHub 9.x.
Only the item types we actually use are implemented.
"""
from __future__ import annotations

import json
import uuid
import zipfile
from pathlib import Path
from typing import Any

NS = "SimHub.Plugins.OutputPlugins.GraphicalDash.Models"


def _type(name: str) -> str:
    return f"{NS}.{name}, SimHub.Plugins"


Radius = int | tuple[int, int, int, int]  # all corners, or (top-left, top-right, bottom-left, bottom-right)


def _border(width: int = 0, color: str = "#FFFFFFFF", radius: Radius = 0) -> dict:
    tl, tr, bl, br = radius if isinstance(radius, tuple) else (radius,) * 4
    return {
        "BorderColor": color,
        "BorderTop": width, "BorderBottom": width, "BorderLeft": width, "BorderRight": width,
        "RadiusTopLeft": tl, "RadiusTopRight": tr,
        "RadiusBottomLeft": bl, "RadiusBottomRight": br,
        "Bindings": {},
    }


# ---- bindings ---------------------------------------------------------------

def formula(target: str, expr: str, fmt: str | None = None) -> dict:
    """Property computed from an NCalc expression."""
    b = {"Formula": {"Expression": expr}, "Mode": 2, "TargetPropertyName": target}
    if fmt is not None:
        b["FormatString"] = fmt
    return b


def gradient(target: str, expr: str, stops: list[tuple[float, str]]) -> dict:
    """Color interpolated from the expression value. 2 or 3 stops: (value, #AARRGGBB)."""
    (v0, c0), *mid, (v1, c1) = stops
    b = {
        "Formula": {"Expression": expr},
        "StartColor": c0, "StartColorValue": v0,
        "EndColor": c1, "EndColorValue": v1,
        "EnableMiddleColor": bool(mid),
        "MiddleColor": mid[0][1] if mid else "#FF000000",
        "MiddleColorValue": mid[0][0] if mid else 0.0,
        "Mode": 4, "TargetPropertyName": target,
    }
    return b


# ---- items ------------------------------------------------------------------

def _base(kind: str, name: str, x: float, y: float, w: float, h: float,
          bindings: list[dict] | None, **extra: Any) -> dict:
    item = {
        "$type": _type(kind),
        "Rotation": 0.0, "UseRotation": False, "CanResize": True,
        "BackgroundColor": "#00FFFFFF", "BlurRadius": 0.0, "EnableBlur": False,
        "BorderStyle": _border(),
        "Left": float(x), "Top": float(y), "Width": float(w), "Height": float(h),
        "Opacity": 100.0, "Visible": True,
        "BlinkDelay": 250.0, "BlinkEnabled": False,
        "BorderBottom": 0, "BorderColor": "#FFFFFFFF", "BorderLeft": 0, "BorderRight": 0, "BorderTop": 0,
        "Id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"simhub-dashboards/{name}")),
        "IsFreezed": False, "IsSelected": False, "Name": name,
        "RenderingSkip": 0, "Sid": 0,
        "Bindings": {b["TargetPropertyName"]: b for b in (bindings or [])},
    }
    item.update(extra)
    return item


def rect(name: str, x, y, w, h, color: str = "#00FFFFFF", radius: Radius = 0,
         border: tuple[int, int, int, int] | None = None, border_color: str = "#FFFFFFFF",
         rotation: str | None = None, bindings: list[dict] | None = None, **extra) -> dict:
    """Rectangle. border=(top, bottom, left, right) widths.
    rotation: expression in degrees; the rectangle rotates around its own center."""
    bindings = list(bindings or [])
    if rotation is not None:
        bindings.append(formula("Rotation", rotation))
    it = _base("RectangleItem", name, x, y, w, h, bindings, IsRectangleItem=True, **extra)
    it["BackgroundColor"] = color
    it["BorderStyle"] = _border(radius=radius)
    if border:
        t, b, l, r = border
        it["BorderStyle"].update(BorderColor=border_color, BorderTop=t, BorderBottom=b,
                                 BorderLeft=l, BorderRight=r)
        it.update(BorderColor=border_color, BorderTop=t, BorderBottom=b, BorderLeft=l, BorderRight=r)
    if rotation is not None:
        it["UseRotation"] = True
    return it


def ellipse(name: str, x, y, w, h, color: str = "#FFFFFFFF", thickness: float = 2,
            fill: str = "#00FFFFFF", bindings: list[dict] | None = None) -> dict:
    """Ring (or filled circle) inside the given box."""
    return _base("EllipseItem", name, x, y, w, h, bindings,
                 FillColor=fill, EllipseColor=color, EllipseThickness=float(thickness),
                 EllipseBackgroundImage="None")


def text(name: str, x, y, w, h, value: str = "", size: float = 12, color: str = "#FFFFFFFF",
         bold: bool = False, align: str = "center", font: str = "Segoe UI",
         bindings: list[dict] | None = None, **extra) -> dict:
    halign = {"left": 0, "center": 1, "right": 2}[align]
    return _base(
        "TextItem", name, x, y, w, h, bindings,
        IsTextItem=True, ShadowDepth=0, ShadowBlur=0, ShadowDirection=315, ShadowColor="#FF808080",
        Font=font, FontWeight="Bold" if bold else "Normal", TextWrapping=1, FontStyle="Normal",
        FontSize=float(size), Text=value, TextColor=color,
        HorizontalAlignment=halign, VerticalAlignment=1,
        UseMonospacedText=False, CharWidth=40.0, SpecialCharsWidth=20.0, SpecialChars=".,:;",
        TextMask="", TextMaskColor="#FF808080", **extra,
    )


def vbar(name: str, x, y, w, h, color: str, back: str = "#40FFFFFF",
         minimum: float = 0, maximum: float = 100, bindings: list[dict] | None = None) -> dict:
    """Vertical bar gauge filling from the bottom."""
    it = _base(
        "VerticalLinearGaugeItem", name, x, y, w, h, bindings,
        GaugeAlignment=2, AutoSize=False, AutoSizeScale=1.0, GaugeColor=color,
        Minimum=float(minimum), Maximum=float(maximum), Value=float(maximum), Steps=0.0, PAW=float(h),
    )
    it["BackgroundColor"] = back
    return it


def hbar(name: str, x, y, w, h, color: str, back: str = "#40FFFFFF",
         minimum: float = 0, maximum: float = 100, from_right: bool = False,
         bindings: list[dict] | None = None) -> dict:
    """Horizontal bar gauge filling from the left (or from the right with from_right=True).
    Prefer gauges over binding Width: Width bindings did not update in SimHub 9.13."""
    it = _base(
        "LinearGaugeItem", name, x, y, w, h, bindings,
        IsLinearGauge=True, GaugeOrientation=0, GaugeAlignment=2 if from_right else 0,
        BackgroundImage="None", AutoSize=False, GaugeColor=color,
        AlternateGaugeColor=color, UseAlternateStyle=False,
        Minimum=float(minimum), Maximum=float(maximum), Value=0.0, Steps=0.0, PAW=float(w),
    )
    it["BackgroundColor"] = back
    return it


def layer(name: str, items: list[dict], x=0, y=0, w=0, h=0) -> dict:
    it = _base("Layer", name, x, y, w, h, None,
               Repetitions=0.0, RepeatLeftOffset=0.0, RepeatTopOffset=0.0,
               ShowSelection=False, Group=False)
    del it["IsFreezed"]  # SimHub does not write it for layers
    it["Childrens"] = items
    return it


# ---- scaling ----------------------------------------------------------------

def scale(items: list[dict], sx: float, sy: float | None = None) -> list[dict]:
    """Scale positions/sizes in place (x by sx, y by sy). Fonts, radii and line widths use min(sx, sy)."""
    sy = sx if sy is None else sy
    s = min(sx, sy)

    def walk(it: dict) -> None:
        paw = sx if it.get("IsLinearGauge") else sy  # gauge length: horizontal vs vertical gauge
        for k, f in (("Left", sx), ("Width", sx), ("Top", sy), ("Height", sy), ("PAW", paw),
                     ("FontSize", s), ("EllipseThickness", s)):
            if k in it:
                it[k] = round(it[k] * f, 1)
        for d in (it, it.get("BorderStyle", {})):
            for k in [k for k in d if k.startswith(("Border", "Radius")) and isinstance(d[k], int)]:
                d[k] = round(d[k] * s)
        for child in it.get("Childrens", []):
            walk(child)

    for it in items:
        walk(it)
    return items


# ---- dashboard --------------------------------------------------------------

def dashboard(title: str, description: str, author: str, width: int, height: int,
              items: list[dict], background: str = "#00000000") -> dict:
    meta = {
        "Title": title, "Description": description, "Author": author,
        "ScreenCount": 1.0, "InGameScreensIndexs": [0], "IdleScreensIndexs": [],
        "MainPreviewIndex": 0, "IsOverlay": True, "ShowInTaskBar": True,
        "Width": float(width), "Height": float(height), "OverlaySizeWarning": False,
        "MetadataVersion": 2.0, "EnableOnDashboardMessaging": True, "PitScreensIndexs": [],
    }
    screen = {
        "RenderingSkip": 0, "IsFreezed": False, "InGameScreen": True, "IdleScreen": False,
        "PitScreen": False, "ScreenScript": {"Interpreter": 1}, "BackgroundColor": background,
        "IsSelected": True, "Id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"simhub-dashboards/{title}/screen")),
        "Name": "Screen1", "Sid": 0, "Items": items, "Bindings": {},
    }
    return {
        "Version": 2, "Id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"simhub-dashboards/{title}")),
        "BaseHeight": height, "BaseWidth": width, "BackgroundColor": "#FF000000",
        # $id "3" = the screen (1 = dashboard, 2 = Screens list wrapper), as SimHub writes it
        "Screens": [screen], "SelectedScreen": {"$ref": "3"}, "SnapToGrid": True, "HideLabels": True,
        "ShowBoundingRectangles": False, "GridSize": 10, "Images": [], "Metadata": meta,
        "ShowOnScreenControls": True, "ShowInTaskBar": True, "IsOverlay": True,
        "EnableClickThroughOverlay": True, "EnableOnDashboardMessaging": True,
    }, meta


def _with_ids(obj: Any, counter: list[int]) -> Any:
    """Add Newtonsoft $id to every object and wrap lists as {$id, $values}."""
    if isinstance(obj, dict):
        if "$ref" in obj:  # reference to an object that already has an $id
            return obj
        counter[0] += 1
        out = {"$id": str(counter[0])}
        if "$type" in obj:
            out["$type"] = obj["$type"]
        for k, v in obj.items():
            if k != "$type":
                out[k] = _with_ids(v, counter)
        return out
    if isinstance(obj, list):
        if all(isinstance(v, (int, float)) for v in obj):
            counter[0] += 1
            return {"$id": str(counter[0]), "$values": obj}
        counter[0] += 1
        wrapper = {"$id": str(counter[0])}
        wrapper["$values"] = [_with_ids(v, counter) for v in obj]
        return wrapper
    return obj


def write_simhubdash(dash: dict, meta: dict, name: str, out_dir: Path) -> Path:
    """Write <name>.simhubdash (zip with <name>/<name>.djson + metadata)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    djson = json.dumps(_with_ids(dash, [0]), ensure_ascii=False, indent=2)
    metadata = json.dumps(meta, ensure_ascii=False, indent=2)
    path = out_dir / f"{name}.simhubdash"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for arcname, data in ((f"{name}/{name}.djson", djson), (f"{name}/{name}.djson.metadata", metadata)):
            # fixed timestamp: unchanged dashboards produce byte-identical files (clean git diffs)
            info = zipfile.ZipInfo(arcname, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0  # as on Windows, so Linux builds match too
            z.writestr(info, data)
    return path
