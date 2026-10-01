#!/usr/bin/env python3
"""
check.py — Kiểm tra tính nhất quán của repo Network Mentor.

Chạy:  python check.py          (từ thư mục gốc repo)
       python check.py -v       (in cả những mục đã PASS)

Không cần cài gì thêm. Thoát với mã 1 nếu có lỗi → dùng được trong CI/pre-commit.

Script này KHÔNG chấm nội dung đúng/sai về mặt kỹ thuật.
Nó bắt loại lỗi mà đọc bằng mắt rất khó thấy: tham chiếu chéo lệch nhau,
số trùng, bảng không khớp, output quên dán nhãn.
"""

import os
import re
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

# Dải số LAB cấp cho từng phase — khớp với labs/README.md
LAB_BLOCKS = {0: (1, 9), 1: (10, 19), 2: (20, 29), 3: (30, 39),
              4: (40, 49), 5: (50, 59), 6: (60, 69), 7: (70, 79)}
FINAL_LAB = 99

PHASE_DIRS = {
    0: "00-foundation", 1: "01-switching", 2: "02-routing", 3: "03-services",
    4: "04-ipv6", 5: "05-wireless", 6: "06-security", 7: "07-wan-vpn",
}

problems = []
passed = []


def fail(check, msg):
    problems.append((check, msg))


def ok(check, msg):
    passed.append((check, msg))


def md_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for f in sorted(filenames):
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def section(text, start_marker, stop_prefix="\n## "):
    """Lấy phần text từ start_marker tới heading kế tiếp."""
    i = text.find(start_marker)
    if i == -1:
        return None
    rest = text[i + len(start_marker):]
    j = rest.find(stop_prefix)
    return rest if j == -1 else rest[:j]


# ─────────────────────────────────────────────────────────────────────────────
# 1. Link nội bộ không hỏng
# ─────────────────────────────────────────────────────────────────────────────
def check_links():
    pat = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    bad = 0
    for p in md_files():
        base = os.path.dirname(p)
        for m in pat.finditer(read(p)):
            link = m.group(1).strip()
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = link.split("#")[0]
            if not target:
                continue
            # placeholder trong templates: lesson-NN-....md, ../NN-phase/...
            if "NN" in target:
                continue
            if not os.path.exists(os.path.normpath(os.path.join(base, target))):
                fail("link", f"{rel(p)} → {link}")
                bad += 1
    if not bad:
        ok("link", "mọi link nội bộ đều trỏ tới file có thật")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Output thiết bị phải dán nhãn "output điển hình"
#    (nguyên tắc 3.7 của MENTOR_PROMPT)
# ─────────────────────────────────────────────────────────────────────────────
def check_output_labels():
    device = re.compile(r"(^[A-Za-z0-9_-]+[#>]\s|%[A-Z0-9]+-\d-)", re.M)
    bad = 0
    for p in md_files():
        for block in re.findall(r"^```text\n(.*?)^```", read(p), re.S | re.M):
            if device.search(block) and "điển hình" not in block:
                first = next((l for l in block.splitlines() if l.strip()), "")
                fail("nhãn-output", f"{rel(p)}: {first[:60]}")
                bad += 1
    if not bad:
        ok("nhãn-output", "mọi block output thiết bị đều có nhãn tự-verify")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Bảng lệnh điều khiển: README phải khớp MENTOR_PROMPT
# ─────────────────────────────────────────────────────────────────────────────
def check_command_tables():
    def cmds(path, marker):
        body = section(read(os.path.join(ROOT, path)), marker)
        if body is None:
            fail("bảng-lệnh", f"không tìm thấy bảng lệnh trong {path}")
            return None
        return set(re.findall(r"^\| `([^`]+)`", body, re.M))

    a = cmds("README.md", "### Lệnh điều khiển AI giữa buổi")
    b = cmds("MENTOR_PROMPT.md", "### Lệnh điều khiển tôi có thể gõ")
    if a is None or b is None:
        return
    if a != b:
        for c in sorted(a - b):
            fail("bảng-lệnh", f"`{c}` có trong README nhưng thiếu ở MENTOR_PROMPT")
        for c in sorted(b - a):
            fail("bảng-lệnh", f"`{c}` có trong MENTOR_PROMPT nhưng thiếu ở README")
    else:
        ok("bảng-lệnh", f"2 bảng khớp nhau ({len(a)} lệnh)")

    # Lệnh mentor được nhắc ở file khác phải đã khai báo trong prompt.
    # Chỉ xét khi câu văn nói về AI mentor — tránh nhầm với lệnh Cisco
    # ("gõ `shutdown`") hay filter Wireshark ("gõ `ip.addr == ...`").
    for p in md_files():
        if rel(p) in ("README.md", "MENTOR_PROMPT.md"):
            continue
        text = read(p)
        for m in re.finditer(r"gõ \*?\*?`([^`]+)`", text):
            c = m.group(1)
            around = text[max(0, m.start() - 100): m.end() + 100]
            is_mentor_context = re.search(r"\bAI\b|mentor", around)
            looks_like_cli = re.search(r"[=/.()\[\]]|^(show|no|ip|switchport|spanning-tree|interface)\b", c)
            if is_mentor_context and not looks_like_cli and c not in b:
                fail("bảng-lệnh", f"{rel(p)} bảo gõ `{c}` nhưng prompt chưa khai báo lệnh này")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Entry assessment: mỗi cụm 5–7 câu, đánh số liên tục
# ─────────────────────────────────────────────────────────────────────────────
def check_assessment():
    path = os.path.join(ROOT, "assessment", "entry-assessment.md")
    if not os.path.exists(path):
        fail("assessment", "thiếu assessment/entry-assessment.md")
        return
    text = read(path).split("## 📊")[0]
    parts = re.split(r"^## (CỤM[^\n]*)", text, flags=re.M)[1:]
    total, bad = 0, 0
    for head, body in zip(parts[0::2], parts[1::2]):
        n = len(re.findall(r"^\d+\. ", body, re.M))
        total += n
        if not 5 <= n <= 7:
            fail("assessment", f"{head.strip()} có {n} câu — prompt §14 yêu cầu 5–7 câu/cụm")
            bad += 1
        declared = re.search(r"\((\d+) câu\)", head)
        if declared and int(declared.group(1)) != n:
            fail("assessment", f"{head.strip()} khai {declared.group(1)} nhưng đếm được {n}")
            bad += 1
    nums = [int(x) for x in re.findall(r"^(\d+)\. ", text, re.M)]
    if nums != list(range(1, len(nums) + 1)):
        fail("assessment", "số thứ tự câu hỏi không liên tục 1..N")
        bad += 1
    if not 20 <= total <= 30:
        fail("assessment", f"tổng {total} câu — prompt §14 yêu cầu 20–30")
        bad += 1
    if not bad:
        ok("assessment", f"{len(parts)//2} cụm, {total} câu, đánh số liên tục")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Số lesson: ROADMAP ≡ README từng phase ≡ PROGRESS
# ─────────────────────────────────────────────────────────────────────────────
def check_lesson_counts():
    roadmap = read(os.path.join(ROOT, "ROADMAP.md"))
    declared = {}
    for m in re.finditer(r"^\| (\d) \| [^|]+\| (\d+) \|", roadmap, re.M):
        declared[int(m.group(1))] = int(m.group(2))
    if not declared:
        fail("lesson-count", "không đọc được bảng tổng quan trong ROADMAP.md")
        return

    bad = 0
    for phase, folder in PHASE_DIRS.items():
        p = os.path.join(ROOT, folder, "README.md")
        if not os.path.exists(p):
            fail("lesson-count", f"thiếu {folder}/README.md")
            bad += 1
            continue
        body = section(read(p), "## 📚 Danh sách lesson")
        if body is None:
            fail("lesson-count", f"{folder}/README.md thiếu mục 'Danh sách lesson'")
            bad += 1
            continue
        n = len(re.findall(r"^\| (\d{2}) \|", body, re.M))
        want = declared.get(phase)
        if want is not None and n != want:
            fail("lesson-count",
                 f"Phase {phase}: ROADMAP khai {want} lesson, {folder}/README liệt kê {n}")
            bad += 1

    # PROGRESS: ô vuông và mẫu số phải khớp
    prog = section(read(os.path.join(ROOT, "PROGRESS.md")), "## 📈 Tiến độ theo phase") or ""
    for m in re.finditer(r"^\| (\d) \| [^|]+\| ([⬜🟩]+) (\d+)/(\d+) \|", prog, re.M):
        phase, boxes, done, tot = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))
        want = declared.get(phase)
        if len(boxes) != tot:
            fail("lesson-count", f"PROGRESS Phase {phase}: {len(boxes)} ô nhưng mẫu số là {tot}")
            bad += 1
        if want is not None and tot != want:
            fail("lesson-count", f"PROGRESS Phase {phase}: mẫu số {tot} ≠ ROADMAP {want}")
            bad += 1
        if done > tot:
            fail("lesson-count", f"PROGRESS Phase {phase}: {done}/{tot} — tử số lớn hơn mẫu")
            bad += 1
    if not bad:
        ok("lesson-count", "ROADMAP ≡ README từng phase ≡ PROGRESS")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Số LAB: không trùng, nằm đúng dải của phase
# ─────────────────────────────────────────────────────────────────────────────
def check_labs():
    bad = 0
    # 6a. cùng số LAB không được mang 2 tên khác nhau
    titles = defaultdict(set)
    for p in md_files():
        for m in re.finditer(r"LAB (\d{2})\s*[—–-]\s*([^\n*|\]]+)", read(p)):
            titles[m.group(1)].add(m.group(2).strip().rstrip("*").strip()[:40].lower())
    for num, names in sorted(titles.items()):
        if len(names) > 1:
            fail("lab-số", f"LAB {num} được dùng cho {len(names)} nội dung khác nhau: {sorted(names)}")
            bad += 1

    # 6b. index trong labs/README: số lab phải nằm đúng dải phase
    idx = section(read(os.path.join(ROOT, "labs", "README.md")), "## 📋 Index") or ""
    indexed = set()
    for m in re.finditer(r"^\| (\d{2}) \|[^|]+\|\s*(\d)\s*\|", idx, re.M):
        num, phase = int(m.group(1)), int(m.group(2))
        indexed.add(num)
        lo, hi = LAB_BLOCKS.get(phase, (0, 0))
        if num != FINAL_LAB and not lo <= num <= hi:
            fail("lab-số", f"LAB {num:02d} gán cho Phase {phase} nhưng dải của phase này là {lo:02d}–{hi:02d}")
            bad += 1

    # 6c. file lab trên đĩa phải có trong index
    for f in sorted(os.listdir(os.path.join(ROOT, "labs"))):
        m = re.match(r"lab(\d{2})-", f)
        if m and int(m.group(1)) not in indexed:
            fail("lab-số", f"labs/{f} tồn tại nhưng không có trong Index của labs/README.md")
            bad += 1
    if not bad:
        ok("lab-số", f"không trùng số, nằm đúng dải phase ({len(indexed)} lab trong index)")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Quy ước đặt tên file
# ─────────────────────────────────────────────────────────────────────────────
def check_naming():
    bad = 0
    for phase, folder in PHASE_DIRS.items():
        d = os.path.join(ROOT, folder)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md") or f in ("README.md",):
                continue
            if f.startswith("review-phase"):
                continue
            if not re.fullmatch(r"lesson-\d{2}-[a-z0-9-]+\.md", f):
                fail("đặt-tên", f"{folder}/{f} — phải là lesson-NN-ten-khong-dau.md")
                bad += 1
    for f in sorted(os.listdir(os.path.join(ROOT, "labs"))):
        if f.endswith(".md") and f != "README.md" and not re.fullmatch(r"lab\d{2}-[a-z0-9-]+\.md", f):
            fail("đặt-tên", f"labs/{f} — phải là labNN-ten-khong-dau.md")
            bad += 1
    if not bad:
        ok("đặt-tên", "mọi file lesson/lab theo đúng quy ước")


# ─────────────────────────────────────────────────────────────────────────────
# 8. File mà MENTOR_PROMPT nhắc tới phải tồn tại
# ─────────────────────────────────────────────────────────────────────────────
def check_prompt_refs():
    text = read(os.path.join(ROOT, "MENTOR_PROMPT.md"))
    bad = 0
    for m in re.finditer(r"`([a-zA-Z0-9_./-]+\.md)`", text):
        t = m.group(1)
        if "NN" in t:
            continue
        if not os.path.exists(os.path.join(ROOT, t)):
            fail("prompt-ref", f"MENTOR_PROMPT nhắc `{t}` nhưng file không tồn tại")
            bad += 1
    if not bad:
        ok("prompt-ref", "mọi file MENTOR_PROMPT nhắc tới đều có thật")


# ─────────────────────────────────────────────────────────────────────────────
def main():
    for fn in (check_links, check_output_labels, check_command_tables,
               check_assessment, check_lesson_counts, check_labs,
               check_naming, check_prompt_refs):
        try:
            fn()
        except Exception as e:                                  # noqa: BLE001
            fail(fn.__name__, f"script lỗi khi chạy: {e!r}")

    print()
    print("  NETWORK MENTOR — kiểm tra nhất quán repo")
    print("  " + "─" * 58)

    if VERBOSE or not problems:
        for check, msg in passed:
            print(f"  \033[32m✓\033[0m {check:<14} {msg}")

    if problems:
        print()
        grouped = defaultdict(list)
        for check, msg in problems:
            grouped[check].append(msg)
        for check in sorted(grouped):
            print(f"  \033[31m✗\033[0m {check}")
            for msg in grouped[check]:
                print(f"      {msg}")

    print("  " + "─" * 58)
    if problems:
        print(f"  \033[31m{len(problems)} lỗi\033[0m · {len(passed)} mục đạt")
        print("  Sửa xong chạy lại: python check.py")
        print()
        return 1
    print(f"  \033[32mOK — {len(passed)}/{len(passed)} mục đạt, không có lỗi.\033[0m")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
