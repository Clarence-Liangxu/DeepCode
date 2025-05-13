#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

url = "https://developer.arm.com/architectures/instruction-sets/intrinsics/vaddq_s64"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# 尝试查找伪码所在位置
pre = soup.select_one("section.code-operations pre")

if pre:
    print("✅ 找到伪码：\n")
    print(pre.text[:300])  # 只打印前 300 字
else:
    print("❌ 页面中未找到伪码 <pre> 标签")
