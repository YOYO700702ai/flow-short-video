"""驗收 Flow 下載回來的片段：縮圖總表、長度、停格、講的是哪一種語言。

用法：
    python <技能資料夾>/scripts/check.py <作品資料夾>/片段
    python <技能資料夾>/scripts/check.py <作品資料夾>/片段/S5_360p.mp4      （只驗一支）
    python <技能資料夾>/scripts/check.py <作品資料夾>/片段 --模型 medium     （辨識比較準、比較慢）
    python <技能資料夾>/scripts/check.py <作品資料夾>/片段 --同角色 大哥=S2,S6 媽媽=S2,S4
        （把同一個角色各鏡講話的部分接成一支試聽檔：驗收/試聽_大哥.wav，聽是不是同一個聲音）
    python <技能資料夾>/scripts/check.py <作品資料夾>/片段 --有台詞 S1,S2,S4,S5
        （列出提示詞裡有寫中文原文的鏡（台詞或旁白）。只有這幾鏡要求一定是中文；
          沒列到的鏡辨識出外文，多半是音效被當成講話，報告會註明不算錯）

輸出：
- 片段資料夾旁邊的「驗收」資料夾（片段_段02 就是 驗收_段02）：每支一張縮圖總表（<檔名>_總表.jpg，8 格照時間排），
  以及一份 驗收報告.md（Codex 讀這份來判斷要不要重跑）。
- 終端機也會印出同樣的表。

語音：
- 有裝 faster-whisper（建議，pip install faster-whisper）或 openai-whisper，就會自動判斷語言、列出每句話和時間。
- **不會強制指定語言。** 強制設成中文的話，英文會被直接翻成中文，看起來像全對。
- 都沒裝就略過，報告裡會提醒「請自己戴耳機聽」。
- 沒有人聲的片段，辨識程式常會亂寫一句「Thanks for watching!」「다음 영상에서 만나요!」之類的，那不是真的有人講話。
  加 --有台詞 列出有台詞的鏡，就只檢查那幾鏡是不是中文。

停格：用 ffmpeg 的 freezedetect 找「畫面幾乎不動超過 0.4 秒」的地方，開頭或結尾的停格通常剪掉就好，中間的才要重跑。
"""
import shutil
import subprocess
import sys
from pathlib import Path


def need_ffmpeg():
    for exe in ("ffmpeg", "ffprobe"):
        if shutil.which(exe) is None:
            sys.exit(f"找不到 {exe}。請先安裝 ffmpeg（Windows：winget install Gyan.FFmpeg），裝好後重開 Codex 再試。")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,duration",
                          "-of", "compact=p=0:nk=0", str(path)], capture_output=True, text=True).stdout
    info = {"有聲音": False}
    for line in out.splitlines():
        kv = dict(x.split("=", 1) for x in line.split("|") if "=" in x)
        if kv.get("codec_type") == "video":
            info["寬"], info["高"] = kv.get("width"), kv.get("height")
            info["長度"] = float(kv.get("duration", 0) or 0)
        elif kv.get("codec_type") == "audio":
            info["有聲音"] = True
    return info


def sheet(path, dur, out):
    """8 格縮圖照時間排成 4×2"""
    rate = 8 / max(dur, 0.5)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(path), "-vf",
                    f"fps={rate:.4f},scale=360:-1,tile=4x2", "-frames:v", "1", str(out)], check=True)


def freezes(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vf", "freezedetect=n=0.003:d=0.4",
                        "-map", "0:v:0", "-f", "null", "-"], capture_output=True, text=True)
    found, start = [], None
    for line in r.stderr.splitlines():
        if "freeze_start" in line:
            start = float(line.rsplit(":", 1)[1])
        elif "freeze_end" in line and start is not None:
            found.append((start, float(line.rsplit(":", 1)[1])))
            start = None
    if start is not None:
        found.append((start, None))
    return found


def load_asr(size="small"):
    """size：辨識模型大小，small 比較快；電腦夠力可以用 --模型 medium 比較準"""
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(size, device="cpu", compute_type="int8")

        def run(path):
            segs, info = model.transcribe(str(path), vad_filter=False, word_timestamps=True)
            out = []
            for s in segs:   # 用逐字時間：第一個字開始到最後一個字結束，排剪接點比較準
                a, b = (s.words[0].start, s.words[-1].end) if s.words else (s.start, s.end)
                out.append((a, b, s.text.strip()))
            return info.language, info.language_probability, out
        return "faster-whisper", run
    except ImportError:
        pass
    try:
        import whisper
        model = whisper.load_model(size)

        def run(path):
            audio = whisper.pad_or_trim(whisper.load_audio(str(path)))
            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            _, probs = model.detect_language(mel)
            lang = max(probs, key=probs.get)
            r = model.transcribe(str(path), fp16=False, word_timestamps=True)
            out = []
            for s in r["segments"]:   # 用逐字時間：第一個字開始到最後一個字結束
                w = s.get("words") or []
                a, b = (w[0]["start"], w[-1]["end"]) if w else (s["start"], s["end"])
                out.append((a, b, s["text"].strip()))
            return lang, probs[lang], out
        return "openai-whisper", run
    except ImportError:
        return None, None


LANG = {"zh": "中文", "en": "英文", "ja": "日文", "ko": "韓文"}


def parse_groups(argv):
    """--同角色 大哥=S2,S6 媽媽=S2,S4  →  {"大哥": ["S2", "S6"], "媽媽": ["S2", "S4"]}"""
    if "--同角色" not in argv:
        return {}
    groups = {}
    for tok in argv[argv.index("--同角色") + 1:]:
        if tok.startswith("--"):
            break
        if "=" in tok:
            name, shots = tok.split("=", 1)
            groups[name] = [s.strip() for s in shots.replace("，", ",").split(",") if s.strip()]
    return groups


def parse_list(argv, flag):
    """--有台詞 S1,S2 S4  →  {"S1", "S2", "S4"}；沒給這個選項就回傳 None"""
    if flag not in argv:
        return None
    found = set()
    for tok in argv[argv.index(flag) + 1:]:
        if tok.startswith("--"):
            break
        found |= {s.strip() for s in tok.replace("，", ",").split(",") if s.strip()}
    return found


def shot_id(path):
    """S2_720p.mp4 → S2"""
    return path.stem.split("_", 1)[0]


def find_clip(folder, shot):
    """鏡號 S2 → 片段資料夾裡的 S2_720p.mp4（沒有就 S2_360p.mp4，再沒有就 S2_ 開頭的第一支）"""
    for suffix in ("_720p.mp4", "_360p.mp4"):
        p = folder / f"{shot}{suffix}"
        if p.exists():
            return p
    found = sorted(folder.glob(f"{shot}_*.mp4"))
    return found[0] if found else None


def voice_montages(groups, folder, out_dir, speech, asr):
    """把同一個角色在各鏡講話的部分接成一支試聽檔（中間隔 0.6 秒），讓人一次聽完比對是不是同一個聲音。
    Flow 每一鏡是獨立配音，沒有綁角色聲音時，同一個角色每鏡都可能不一樣。用耳朵判斷：
    平靜講話和大叫的差異會蓋過「是不是同一個人」，所以不要用數字比。"""
    lines = ["## 同一角色試聽（請戴耳機聽：聽起來要像同一個人）", ""]
    for name, shots in groups.items():
        parts = []
        for shot in shots:
            clip = find_clip(folder, shot)
            if clip is None:
                lines.append(f"- {name}：找不到 {shot} 的片段，略過")
                continue
            segs = speech.get(clip.name)
            if segs is None and asr:
                lang, prob, s = asr(clip)
                segs = s if (lang == "zh" or prob >= 0.7) else []
            dur = probe(clip).get("長度", 0)
            if segs:
                a = max(0.0, min(x[0] for x in segs) - 0.15)
                b = min(dur, max(x[1] for x in segs) + 0.25)
            else:
                a, b = 0.0, dur    # 沒辨識到人聲（或沒裝辨識）就整支放進去
            parts.append((clip, a, b))
        if not parts:
            continue
        out = out_dir / f"試聽_{name}.wav"
        args, fc = ["ffmpeg", "-y", "-v", "error"], []
        for i, (clip, a, b) in enumerate(parts):
            args += ["-ss", f"{a:.2f}", "-t", f"{b - a:.2f}", "-i", str(clip)]
            fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
        labels = []
        for i in range(len(parts)):
            labels.append(f"[a{i}]")
            if i < len(parts) - 1:
                fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:0.6[g{i}]")
                labels.append(f"[g{i}]")
        fc.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1[out]")
        subprocess.run(args + ["-filter_complex", ";".join(fc), "-map", "[out]", str(out)], check=True)
        desc = "、".join(f"{c.stem} {a:.1f}～{b:.1f} 秒" for c, a, b in parts)
        lines.append(f"- {name}：{out_dir.name}/{out.name}（{desc}）")
    lines.append("")
    lines.append("不像同一個人時：確認那幾鏡的提示詞最前面有沒有用 @ 插入角色，以及角色有沒有在 Flow 綁好聲音，再重跑那一鏡。")
    lines.append("")
    return lines


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    need_ffmpeg()
    target = Path(sys.argv[1]).resolve()
    files = sorted(target.glob("*.mp4")) if target.is_dir() else [target]
    if not files:
        sys.exit(f"{target} 裡沒有 mp4")
    clips_dir = target if target.is_dir() else target.parent
    # 片段 → 驗收；片段_段02 → 驗收_段02（一部作品有好幾段時，各段的驗收結果不會互相覆蓋）
    name = clips_dir.name.replace("片段", "驗收", 1) if "片段" in clips_dir.name else "驗收"
    out_dir = clips_dir.parent / name
    out_dir.mkdir(parents=True, exist_ok=True)

    size = sys.argv[sys.argv.index("--模型") + 1] if "--模型" in sys.argv else "small"
    engine, asr = load_asr(size)
    lines = ["# 驗收報告", ""]
    if engine:
        lines.append(f"語音辨識：{engine}（自動判斷語言，沒有強制指定）")
    else:
        lines.append("語音辨識：**沒有安裝**，請自己戴耳機聽每一支，確認台詞是中文、沒有多出來的人聲。"
                     "想自動檢查可以安裝：pip install faster-whisper")
    talk = parse_list(sys.argv, "--有台詞")
    if engine and talk is not None:
        lines.append(f"有台詞的鏡：{'、'.join(sorted(talk)) or '（沒有）'}。只有這幾鏡一定要是中文；"
                     "其他鏡辨識出外文多半是音效被當成講話，不算錯。")
    elif engine:
        lines.append("提示：加 `--有台詞 S1,S2,…` 列出有台詞（含旁白）的鏡，沒台詞的鏡就不會被誤判。")
    lines.append("")
    speech = {}   # 檔名 -> [(開始, 結束, 文字)]，給「同角色試聽」用

    for f in files:
        info = probe(f)
        dur = info.get("長度", 0)
        pic = out_dir / f"{f.stem}_總表.jpg"
        sheet(f, dur, pic)
        fz = freezes(f)
        lines.append(f"## {f.name}")
        lines.append(f"- 長度 {dur:.2f} 秒，{info.get('寬')}×{info.get('高')}，{'有' if info['有聲音'] else '沒有'}聲音")
        lines.append(f"- 縮圖總表：{out_dir.name}/{pic.name}（照時間排 8 格，看動作有沒有照提示詞、角色有沒有變樣）")
        if fz:
            desc = "、".join(f"{a:.1f}～{b:.1f} 秒" if b is not None else f"{a:.1f} 秒到結尾" for a, b in fz)
            lines.append(f"- 停格：{desc}（在開頭或結尾的剪掉就好；在中間的要考慮重跑）")
        else:
            lines.append("- 停格：沒有超過 0.4 秒的")
        if asr and info["有聲音"]:
            lang, prob, segs = asr(f)
            speech[f.name] = segs if (lang == "zh" or prob >= 0.7) else []
            name = LANG.get(lang, lang)
            if not segs:
                lines.append("- 人聲：沒聽到（只有音效或環境聲）")
                lines.append("")
                continue
            silent_shot = talk is not None and shot_id(f) not in talk
            if silent_shot and lang != "zh":
                note = ("  （這鏡沒有台詞：辨識出的外文多半是音效或雜音被當成講話，不算錯；"
                        "有疑慮再自己聽一下）")
            elif silent_shot:
                note = "  （這鏡應該沒有台詞，卻聽到中文：請自己聽一下，是不是多出一句不該有的人聲）"
            elif lang == "zh":
                note = ""
            elif prob < 0.7:
                note = ("  （不太確定：通常是片段裡沒有人聲、只有音效，辨識程式在亂猜。請自己聽一下，"
                        "沒有人講話就不用管）")
            else:
                note = "  ⚠ 不是中文！檢查提示詞是不是每個會出聲的地方都寫了 in Mandarin Chinese: 原文"
            lines.append(f"- 判斷語言：{name}（{prob:.0%}）{note}")
            for a, b, txt in segs:
                lines.append(f"  - {a:.1f}～{b:.1f} 秒：{txt}")
        lines.append("")

    groups = parse_groups(sys.argv)
    if groups:
        folder = target if target.is_dir() else target.parent
        lines += voice_montages(groups, folder, out_dir, speech, asr)

    report = out_dir / "驗收報告.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\n報告：{report}")


if __name__ == "__main__":
    main()
