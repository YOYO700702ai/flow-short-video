"""把 Flow 生成的片段照分鏡剪成一段，燒上字幕。

用法：
    python <技能資料夾>/scripts/cut.py <作品資料夾>/06_剪接設定.json
    python <技能資料夾>/scripts/cut.py <作品資料夾>/06_剪接設定.json --只看時間表

設定檔格式見 <技能資料夾>/assets/templates/06_剪接設定.json。只需要 Python 3.9 以上和 ffmpeg，不用另外安裝套件。

做了什麼：
- 每一鏡從片段的「從第幾秒」開始取「取幾秒」。
  - 「從第幾秒」沒寫：用設定檔最上面的「每鏡從第幾秒」（範本是 0.3，跳過 Flow 片段開頭幾乎不動的那一下）。
  - 「取幾秒」沒寫：取到片段結尾。
  - 「檔案」只寫鏡號（例 "S1"）：片段資料夾裡有 S1_720p.mp4 就用它，沒有就用 S1_360p.mp4。
- 字幕兩種寫法，可以混用：
  - 每一鏡自己的 "字幕"：時間寫「在這支片段裡的秒數」（直接抄驗收報告的講話時間），程式換算成在成品裡的位置。
  - 最外層的 "字幕"：時間寫「在成品裡的秒數」。
- 會照片段的實際長度夾住：Flow 的 720p 放大版每支少最後一格（6 秒變 5.958 秒），
  不夾住的話畫面會比聲音短，越後面越對不上嘴。
- 聲音三種：
  - "自己"：用這一鏡片段的原聲。
  - "延續上一鏡"：這一鏡不用自己的聲音，由上一鏡多取的聲音蓋過來（台詞講到一半切去拍聽的人）。
  - "靜音"：這一鏡放無聲。
- 輸出兩支：<輸出檔名>_無字幕.mp4、<輸出檔名>_字幕版.mp4；
  字幕白字黑邊，"旁白" 樣式是淡灰斜體，和台詞分得出來。
- 印出一張時間表：每一鏡在成品裡從第幾秒到第幾秒，排字幕時間用。

字幕字體：
- 設定檔沒寫就用電腦內建的基本中文字體（Windows：微軟正黑體；Mac：蘋方；Linux：Noto Sans CJK TC）。
- 想用自己的字型：設定檔寫 "字幕字型名稱"（字型的英文家族名稱，例 "LXGW WenKai TC"），
  字型沒安裝在電腦上的話，再寫 "字幕字型檔"（.ttf／.otf 的路徑，相對於設定檔所在的資料夾）。
"""
import json
import math
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# 電腦內建的基本中文字體（不用另外下載）
BASIC_FONT = {"Windows": "Microsoft JhengHei", "Darwin": "PingFang TC"}.get(platform.system(), "Noto Sans CJK TC")


def need_ffmpeg():
    for exe in ("ffmpeg", "ffprobe"):
        if shutil.which(exe) is None:
            sys.exit(f"找不到 {exe}。請先安裝 ffmpeg（Windows 可以在終端機輸入：winget install Gyan.FFmpeg），裝好後重開 Codex 再試。")


def length(path):
    """片段的實際長度（秒），用畫面那一軌算"""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        sys.exit(f"讀不到片段長度：{path}\n{out.stderr}")


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(out.stdout.strip())


def find_clip(clips_dir, name):
    """「檔案」寫完整檔名就照用；只寫鏡號（S1）時，先找 S1_720p.mp4，再找 S1_360p.mp4"""
    p = clips_dir / name
    if p.suffix.lower() == ".mp4":
        return p
    for suffix in ("_720p.mp4", "_360p.mp4", ".mp4"):
        q = clips_dir / f"{name}{suffix}"
        if q.exists():
            return q
    return clips_dir / f"{name}_360p.mp4"


def ts(x):
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def wrap(line, n=22):
    """太長的字幕在最靠近中間的標點斷成兩行"""
    if len(line) <= n:
        return line
    cuts = [i + 1 for i, ch in enumerate(line) if ch in "，。？！、；："]
    if not cuts:
        return line
    k = min(cuts, key=lambda i: abs(i - len(line) / 2))
    return line[:k] + r"\N" + line[k:] if k < len(line) else line


def write_ass(subs, path, font_name):
    rows = []
    subs = sorted(subs, key=lambda s: s["開始"])
    for i, s in enumerate(subs):
        a, b = float(s["開始"]), float(s["結束"])
        if i + 1 < len(subs):
            b = min(b, float(subs[i + 1]["開始"]) - 0.05)   # 前後重疊時前一句提早收
        style = "N" if s.get("樣式") == "旁白" else "D"
        rows.append(f"Dialogue: 0,{ts(a)},{ts(b)},{style},,0,0,0,,{wrap(s['文字'])}")
    path.write_text(
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\n\n[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding\n"
        f"Style: D,{font_name},58,&H00FFFFFF,&H00FFFFFF,&H00101010,&H64000000,-1,0,0,0,100,100,2,0,1,3.2,1.2,2,"
        "120,120,64,1\n"
        f"Style: N,{font_name},58,&H00EEEEEE,&H00EEEEEE,&H00303030,&H80000000,0,-1,0,0,100,100,2,0,1,2.4,2.0,2,"
        "120,120,64,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        + "\n".join(rows) + "\n", encoding="utf-8-sig")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cfg_path = Path(sys.argv[1]).resolve()
    only_plan = "--只看時間表" in sys.argv[2:]
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base = cfg_path.parent
    clips_dir = base / cfg.get("片段資料夾", "片段")
    out_dir = base / cfg.get("輸出資料夾", "成品")
    name = cfg.get("輸出檔名", "成品")
    w, h = cfg.get("畫面大小", [1280, 720])
    fps = cfg.get("每秒格數", 24)
    need_ffmpeg()

    default_ss = float(cfg.get("每鏡從第幾秒", 0))
    shots, t, shot_subs = [], 0.0, []
    for i, s in enumerate(cfg["鏡頭"]):
        src = find_clip(clips_dir, s["檔案"])
        if not src.exists():
            sys.exit(f"找不到片段：{src}（檔名要和設定檔的「檔案」一模一樣，或只寫鏡號 S1）")
        L = length(src)
        ss = float(s.get("從第幾秒", default_ss))
        if ss >= L:
            sys.exit(f"{s['鏡']}：從第 {ss} 秒開始，但片段只有 {L:.2f} 秒")
        want = s.get("取幾秒")
        # 長度對齊到整格：畫面只能取整格，聲音照同樣的長度取，鏡頭再多也不會越接越不同步
        max_frames = round(L * fps) - math.ceil(ss * fps - 1e-6)       # 從「從第幾秒」那格起，片段還剩幾格
        if want is None or want == "到結尾":
            want, frames = None, max_frames                            # 沒寫「取幾秒」：取到片段結尾
        else:
            want = float(want)
            first = math.ceil(ss * fps - 1e-6)                         # 取的第一格
            frames = math.ceil((ss + want) * fps - 1e-6) - first       # 落在「從第幾秒」到「從第幾秒＋取幾秒」之間的格數
        dur = min(frames, max_frames) / fps
        sound = s.get("聲音", "自己")
        if sound not in ("自己", "延續上一鏡", "靜音"):
            sys.exit(f"{s['鏡']}：「聲音」只能寫 自己／延續上一鏡／靜音，現在寫的是「{sound}」")
        if sound == "自己" and not has_audio(src):
            print(f"注意：{s['鏡']} 的片段沒有聲音，改成靜音")
            sound = "靜音"
        extra = float(s.get("聲音多取幾秒", 0))
        take = (min(round(dur * fps) + math.ceil(extra * fps - 1e-6), max_frames) / fps) if sound == "自己" else dur
        if want is not None and dur < want - 0.12:   # 720p 放大版本來就少一格（約 0.04～0.09 秒），差更多才提醒
            print(f"注意：{s['鏡']} 想取 {want} 秒，片段從第 {ss} 秒起只剩 {dur:.2f} 秒，已自動夾住")
        # 這一鏡自己的字幕：片段裡的秒數 → 成品裡的秒數
        for sub in s.get("字幕", []):
            a = t + float(sub["開始"]) - ss
            b = t + float(sub["結束"]) - ss
            if a < t - 0.01:
                print(f"注意：{s['鏡']} 的字幕「{sub['文字']}」從片段第 {sub['開始']} 秒開始，"
                      f"比取的起點（第 {ss} 秒）早，已改成從這一鏡開頭出現")
                a = t
            shot_subs.append(dict(sub, 開始=round(a, 2), 結束=round(b, 2)))
        shots.append(dict(i=i, 鏡=s["鏡"], src=src, ss=ss, dur=dur, sound=sound, take=take, 起=t, 訖=t + dur))
        t += dur

    # 檢查「延續上一鏡」有沒有被前一鏡多取的聲音蓋到
    for k, s in enumerate(shots):
        if s["sound"] == "延續上一鏡":
            j = k - 1
            while j >= 0 and shots[j]["sound"] == "延續上一鏡":
                j -= 1
            if j < 0 or shots[j]["sound"] != "自己":
                sys.exit(f"{s['鏡']} 寫了「延續上一鏡」，但前面沒有用自己聲音的鏡頭")
            covered = shots[j]["take"] - shots[j]["dur"]
            need = sum(x["dur"] for x in shots[j + 1:k + 1])
            if covered + 0.05 < need:
                print(f"注意：{shots[j]['鏡']} 多取的聲音只有 {covered:.2f} 秒，蓋不滿後面 {need:.2f} 秒，不足的部分會是無聲。"
                      f"可以把 {shots[j]['鏡']} 的「聲音多取幾秒」加大。")

    print("\n時間表（成品裡的秒數，排字幕用）")
    print("鏡\t成品起\t成品訖\t取片段的\t聲音\t檔案")
    for s in shots:
        print(f"{s['鏡']}\t{s['起']:.2f}\t{s['訖']:.2f}\t{s['ss']:.2f}~{s['ss'] + s['dur']:.2f}\t{s['sound']}\t{s['src'].name}")
    total = shots[-1]["訖"]
    print(f"總長 {total:.2f} 秒\n")
    subs = shot_subs + cfg.get("字幕", [])
    if shot_subs:
        print("各鏡字幕換算到成品裡的時間：")
        for x in shot_subs:
            print(f"  {x['開始']:.2f}～{x['結束']:.2f}　{x['文字']}")
        print()
    if only_plan:
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    args = ["ffmpeg", "-y", "-v", "error"]
    for s in shots:
        args += ["-ss", str(s["ss"]), "-t", str(max(s["take"], s["dur"])), "-i", str(s["src"])]
    vf, af, alabels = [], [], []
    for s in shots:
        i = s["i"]
        vf.append(f"[{i}:v]trim=0:{s['dur']},setpts=PTS-STARTPTS,scale={w}:{h}:flags=lanczos,fps={fps},setsar=1[v{i}]")
        if s["sound"] == "自己":
            af.append(f"[{i}:a]atrim=0:{s['take']},asetpts=PTS-STARTPTS,aresample=48000,"
                      f"aformat=channel_layouts=stereo[a{i}]")
            alabels.append(f"[a{i}]")
        elif s["sound"] == "靜音":
            af.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{s['dur']}[a{i}]")
            alabels.append(f"[a{i}]")
    fc = vf + af
    fc.append("".join(f"[v{s['i']}]" for s in shots) + f"concat=n={len(shots)}:v=1:a=0[v]")
    # 聲音接起來後補齊或切齊到畫面總長，避免頭尾差幾格
    fc.append("".join(alabels) + f"concat=n={len(alabels)}:v=0:a=1,apad,atrim=0:{total:.3f}[a]")
    nosub = out_dir / f"{name}_無字幕.mp4"
    subprocess.run(args + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-movflags", "+faststart", str(nosub)], check=True)
    print("無字幕版：", nosub)

    if not subs:
        print("設定檔沒有字幕，只輸出無字幕版。")
        return
    final = out_dir / f"{name}_字幕版.mp4"
    font_name = cfg.get("字幕字型名稱") or BASIC_FONT
    font_file = cfg.get("字幕字型檔") or ""
    if font_file:
        font_file = (base / font_file).resolve()
        if not font_file.exists():
            sys.exit(f"找不到字幕字型檔：{font_file}（沒有的話把「字幕字型檔」留空，就會用電腦內建的基本字體）")
        if not cfg.get("字幕字型名稱"):
            sys.exit("有指定「字幕字型檔」時，也要寫「字幕字型名稱」（字型的英文家族名稱，例 LXGW WenKai TC）")
    print(f"字幕字體：{font_name}" + (f"（字型檔 {font_file.name}）" if font_file else "（電腦內建）"))
    # 字幕檔和字型先複製到純英文的暫存路徑：ffmpeg 的字幕濾鏡遇到中文路徑容易出錯
    with tempfile.TemporaryDirectory() as td:
        write_ass(subs, Path(td) / "s.ass", font_name)
        esc = td.replace("\\", "/").replace(":", "\\:")
        vf = f"subtitles='{esc}/s.ass'"
        if font_file:
            (Path(td) / "fonts").mkdir()
            shutil.copy2(font_file, Path(td) / "fonts" / font_file.name)
            vf += f":fontsdir='{esc}/fonts'"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(nosub), "-vf", vf, "-c:v", "libx264", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(final)], check=True)
    print("字幕版：", final)


if __name__ == "__main__":
    main()
