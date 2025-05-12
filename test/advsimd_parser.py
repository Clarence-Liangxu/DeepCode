#!/usr/bin/env python3

import re
import json
import argparse
from collections import defaultdict

# https://github.com/ARM-software/acle/blob/main/neon_intrinsics/advsimd.md
# ---------- 工具函数 ----------
def nested_dict():
    return defaultdict(nested_dict)

def convert_to_regular_dict(d):
    if isinstance(d, defaultdict):
        return {k: convert_to_regular_dict(v) for k, v in d.items()}
    return d

def underscore_keys(d):
    if isinstance(d, dict):
        return {k.replace(" ", "_"): underscore_keys(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [underscore_keys(i) for i in d]
    else:
        return d

# ---------- 主逻辑 ----------
def parse_intrinsics(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_titles = ["", "", "", ""]
    intrinsic_tree = nested_dict()

    link_pattern = re.compile(r'<a href="(https://developer\.arm\.com/architectures/instruction-sets/intrinsics/[^"]+)"[^>]*>([^<]+)</a>')
    heading_pattern = re.compile(r'^(#{1,4})\s+(.*)')

    count = 0
    for line in lines:
        heading_match = heading_pattern.match(line)
        if heading_match:
            level = len(heading_match.group(1)) - 1
            title = heading_match.group(2).strip()
            current_titles[level] = title
            for i in range(level + 1, 4):
                current_titles[i] = ""
        else:
            for url, name in link_pattern.findall(line):
                if url.strip():
                    l1, l2, l3, l4 = current_titles
                    node = intrinsic_tree[l1][l2][l3][l4]
                    node.setdefault("intrinsics", []).append({
                        "name": name,
                        "url": url
                    })
                    count += 1

    # 转换为普通 dict，并格式化 key
    regular_tree = convert_to_regular_dict(intrinsic_tree)
    underscored_tree = underscore_keys(regular_tree)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(underscored_tree, f, indent=2, ensure_ascii=False)

    print(f"✅ 已提取 {count} 个 intrinsic，输出文件为: {output_file}")

# ---------- CLI 接口 ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract NEON intrinsics into underscored tree-structured JSON.")
    parser.add_argument("-i", "--input", required=True, help="Input Markdown file (e.g., advsimd.md)")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file (e.g., output_tree_underscored.json)")
    args = parser.parse_args()

    parse_intrinsics(args.input, args.output)
