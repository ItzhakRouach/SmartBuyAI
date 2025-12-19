import asyncio
import json
import os
from playwright.async_api import async_playwright


# --- KSP Semi-Automated Discovery Agent ---
# This script bypasses heavy bot protections (like Cloudflare) by allowing
# a human to handle the navigation and loading, while the script handles
# the heavy lifting of extracting and cleaning structured data.

async def manual_discovery_ksp(category_url):
    """
    Opens a browser for the user to manually load products,
    then extracts all unique product links.
    """
    async with async_playwright() as p:
        # Launch browser in headed mode (visible) so the user can interact
        browser = await p.chromium.launch(headless=False)

        # Set a realistic user agent to mimic a standard browser
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"Target URL: {category_url}")
        print("Navigating to the site...")
        await page.goto(category_url)

        # Instruction block for the developer/user
        print("\n" + "=" * 60)
        print("INTERACTIVE SESSION STARTED:")
        print("1. Please go to the opened browser window.")
        print("2. Solve any Captchas and click 'Show More' until all products are visible.")
        print("3. Return to this terminal and press [ENTER] to extract the data.")
        print("=" * 60 + "\n")

        # Wait for user confirmation before proceeding to extraction
        await asyncio.to_thread(input, "Press ENTER after you finished loading all products...")

        print("Analyzing DOM and extracting product links...")

        # Locate all anchor tags that contain the '/item/' pattern in their href
        # This is a specific pattern for KSP product pages
        all_elements = await page.query_selector_all('a[href*="/item/"]')
        raw_urls = []

        for el in all_elements:
            href = await el.get_attribute("href")
            if href:
                # Cleaning logic:
                # 1. Remove tracking query parameters using split('?')
                # 2. Convert relative paths (/item/123) to absolute URLs
                clean_path = href.split('?')[0]
                full_url = f"https://ksp.co.il{clean_path}" if clean_path.startswith('/') else clean_path
                raw_urls.append(full_url)

        # Convert list to a set to automatically remove duplicate entries
        unique_urls = list(set(raw_urls))

        print(f"Extraction complete! {len(unique_urls)} unique products identified.")

        await browser.close()
        return unique_urls


if __name__ == "__main__":
    # Target: Graphics Cards Category
    ksp_gpu_url = "https://ksp.co.il/web/cat/31635..35..61615"

    # Run the async extraction process
    links = asyncio.run(manual_discovery_ksp(ksp_gpu_url))

    # Save the output to the project's data folder for the next pipeline stage (Orchestrator)
    data_dir = "../../data"
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "ksp_links.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=4)

    print(f"Process finished successfully. Links saved to: {output_path}")