#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright

async def test_clipboard():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 开启窗口便于观察
        page = await browser.new_page()
        await page.goto("https://example.com")
        try:
            copied = await page.evaluate("navigator.clipboard.readText()")
            print(f"✅ 读取剪贴板成功: {copied}")
        except Exception as e:
            print(f"❌ 无法访问剪贴板: {e}")
        await browser.close()

asyncio.run(test_clipboard())
