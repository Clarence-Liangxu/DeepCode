#!/usr/bin/env python3

import json
import csv
import argparse
import threading
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === Configuration ===
RETRIES = 3
WAIT_TIMEOUT = 10
thread_local = threading.local()

# ---------------------------
# Selenium setup (with lightweight config)
# ---------------------------
def get_driver():
    """Each thread reuses one Chrome instance, with resource-saving options."""
    if not hasattr(thread_local, "driver"):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument("--log-level=3")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        thread_local.driver = driver
    return thread_local.driver

# ---------------------------
# Pseudocode Fetch with Retry
# ---------------------------
def get_pseudocode_with_retry(intrinsic, retries=RETRIES):
    url = intrinsic.get("url")
    name = intrinsic.get("name", "UNKNOWN")

    for attempt in range(1, retries + 1):
        try:
            driver = get_driver()
            driver.get(url)

            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section.code-operations pre"))
            )

            pre_tag = driver.find_element(By.CSS_SELECTOR, "section.code-operations pre")
            pseudocode = pre_tag.text.strip()
            return pseudocode, None

        except Exception as e:
            if attempt == retries:
                return None, {
                    "name": name,
                    "url": url,
                    "error": str(e)
                }

# ---------------------------
# JSON Structure Traversal
# ---------------------------
def collect_all_intrinsics(data):
    """Flatten all intrinsic items into a list."""
    intrinsics_list = []
    for category in data["List_of_Intrinsics"].values():
        for group in category.values():
            for operation in group.values():
                for intrinsic in operation["intrinsics"]:
                    intrinsics_list.append(intrinsic)
    return intrinsics_list

# ---------------------------
# Dry-run Mode: URL Reachability Check
# ---------------------------
def dry_run_check_urls(intrinsics, threads=4, output_path="dry_run_failures.json"):
    def check_url(intrinsic):
        name = intrinsic.get("name")
        url = intrinsic.get("url")
        try:
            response = requests.get(url, timeout=10)
            return {
                "name": name,
                "url": url,
                "status": response.status_code,
                "ok": response.status_code == 200
            }
        except Exception as e:
            return {
                "name": name,
                "url": url,
                "status": None,
                "ok": False,
                "error": str(e)
            }

    print(f"🔍 Performing dry-run URL check using {threads} threads...\n")

    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(check_url, intrinsic) for intrinsic in intrinsics]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Dry-run Progress"):
            results.append(future.result())

    total = len(results)
    success = sum(1 for r in results if r["ok"])
    fail = total - success

    print(f"\n✅ Dry-run completed! Total: {total} | Success: {success} | Failures: {fail}")

    failures = [r for r in results if not r["ok"]]
    if failures:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2, ensure_ascii=False)
        print(f"\n⚠️ {len(failures)} unreachable URLs saved to: {output_path}")
    else:
        print("🎉 All URLs are reachable.")

    return results

# ---------------------------
# CSV and Markdown Export
# ---------------------------
def export_to_csv(intrinsics, csv_path):
    with open(csv_path, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "URL", "Pseudocode"])
        for item in intrinsics:
            writer.writerow([item["name"], item["url"], item.get("pseudocode", "")])
    print(f"📝 CSV exported to: {csv_path}")

def export_to_markdown(intrinsics, md_path):
    with open(md_path, "w", encoding="utf-8") as f:
        for item in intrinsics:
            f.write(f"## {item['name']}\n")
            f.write(f"**URL**: [{item['url']}]({item['url']})\n\n")
            code = item.get("pseudocode", "N/A")
            f.write("```c\n" + code + "\n```\n\n")
    print(f"📝 Markdown exported to: {md_path}")

# ---------------------------
# Main CLI Entry
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Fetch ARM intrinsics pseudocode (parallel, optimized).")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file path")
    parser.add_argument("-o", "--output", help="Output JSON with pseudocode")
    parser.add_argument("-f", "--failures", default="failures.json", help="Failed items output path")
    parser.add_argument("-t", "--threads", type=int, default=4, help="Number of parallel threads (default 4)")
    parser.add_argument("--csv", help="Optional CSV export path")
    parser.add_argument("--md", help="Optional Markdown export path")
    parser.add_argument("--dry-run", action="store_true", help="Only test URL accessibility (no scraping)")
    parser.add_argument("--dry-run-output", default="dry_run_failures.json", help="Output path for dry-run failures")
    args = parser.parse_args()

    # Load JSON input
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_intrinsics = collect_all_intrinsics(data)

    # Dry-run mode
    if args.dry_run:
        dry_run_check_urls(all_intrinsics, threads=args.threads, output_path=args.dry_run_output)
        return

    # Pseudocode scraping
    failures = []
    print(f"🚀 Starting parallel pseudocode fetching for {len(all_intrinsics)} intrinsics...\n")

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_map = {
            executor.submit(get_pseudocode_with_retry, intrinsic): intrinsic
            for intrinsic in all_intrinsics
        }

        for future in tqdm(as_completed(future_map), total=len(future_map), desc="Scraping Progress"):
            intrinsic = future_map[future]
            try:
                pseudocode, error = future.result()
                if pseudocode:
                    intrinsic["pseudocode"] = pseudocode
                else:
                    intrinsic["pseudocode"] = "N/A"
                    failures.append(error)
            except Exception as e:
                intrinsic["pseudocode"] = "N/A"
                failures.append({
                    "name": intrinsic.get("name"),
                    "url": intrinsic.get("url"),
                    "error": str(e)
                })

    # Save JSON output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ JSON written to: {args.output}")

    # Save failures
    if failures:
        with open(args.failures, "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2, ensure_ascii=False)
        print(f"⚠️ {len(failures)} failures saved to: {args.failures}")
    else:
        print("🎉 All intrinsics scraped successfully.")

    # Optional exports
    if args.csv:
        export_to_csv(all_intrinsics, args.csv)

    if args.md:
        export_to_markdown(all_intrinsics, args.md)

# ---------------------------
# Run Entry
# ---------------------------
if __name__ == "__main__":
    main()
