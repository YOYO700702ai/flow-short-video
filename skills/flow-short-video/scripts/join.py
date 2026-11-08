"""把剪好的各段接成整支，需要的話另出一支手機版（854×480，檔案小、傳手機看）。

用法：
    python <技能資料夾>/scripts/join.py <輸出.mp4> <段01_字幕版.mp4> <段02_字幕版.mp4> ...
    python <技能資料夾>/scripts/join.py <輸出.mp4> <段01_字幕版.mp4> <段02_字幕版.mp4> ... --手機版

- 照命令列的順序接；每段的畫面大小、每秒格數、聲音取樣率會先統一，再重新編碼接起來（不會接歪、不會有一段沒聲音）。
- 畫面大小和每秒格數用第一段的。
- --手機版：另外輸出 <輸出檔名>_手機版.mp4。
- 只需要 Python 3.9 以上和 ffmpeg。
"""
import shutil
import subprocess
import sys
from pathlib import Path


def need_ffmpeg():
    for exe in ("ffmpeg", "ffprobe"):
        if shutil.which(exe) is None:
            sys.exit(f"找不到 {exe}。請先安裝 ffmpeg（Windows 可以在終端機輸入：winget install Gyan.FFmpeg），裝好後重開 Codex 再試。")


def video_info(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    try:
        w, h, rate = out.split(",")[:3]
        num, den = rate.split("/")
        return int(w), int(h), round(int(num) / int(den), 3)
    except ValueError:
        sys.exit(f"讀不到影片資訊：{path}")


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(out.stdout.strip())


def length(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True)
    return float(out.stdout.strip())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mobile = "--手機版" in sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    need_ffmpeg()
    out = Path(args[0]).resolve()
    parts = [Path(p).resolve() for p in args[1:]]
    for p in parts:
        if not p.exists():
            sys.exit(f"找不到：{p}")
    w, h, fps = video_info(parts[0])

    cmd, fc, labels = ["ffmpeg", "-y", "-v", "error"], [], []
    for i, p in enumerate(parts):
        cmd += ["-i", str(p)]
        fc.append(f"[{i}:v]scale={w}:{h}:flags=lanczos,fps={fps},setsar=1,setpts=PTS-STARTPTS[v{i}]")
        if has_audio(p):
            fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,"
                      f"apad,atrim=0:{length(p):.3f}[a{i}]")
        else:
            fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{length(p):.3f}[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    fc.append("".join(labels) + f"concat=n={len(parts)}:v=1:a=1[v][a]")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
                          "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                          "-movflags", "+faststart", str(out)], check=True)
    print(f"整支（{len(parts)} 段，{length(out):.1f} 秒）：{out}")

    if mobile:
        small = out.with_name(f"{out.stem}_手機版.mp4")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-vf", "scale=854:480:flags=lanczos",
                        "-c:v", "libx264", "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(small)], check=True)
        print(f"手機版（{small.stat().st_size / 1e6:.1f} MB）：{small}")


if __name__ == "__main__":
    main()
