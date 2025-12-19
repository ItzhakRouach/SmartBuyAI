import asyncio
import requests
import json
from playwright.async_api import async_playwright


async def extract_product_information(url):
    """
    Navigates to a product page, extracts raw text, and uses a local
    Llama 3 model to parse structured product data.
    """
    async with async_playwright() as p:
        # 1. BROWSER SETUP
        # headless=False allows you to see the browser while it's working
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"Scanning product: {url}")

        # 2. NAVIGATION
        # 'networkidle' ensures the page is fully loaded before we scrape the text
        await page.goto(url, wait_until='networkidle')

        # 3. CONTENT EXTRACTION
        # Extracting the entire text of the body tag to provide context to the AI
        page_text = await page.inner_text("body")
        await browser.close()

        print("Analyzing product using AI (Ollama/Llama3)....")

        # 4. AI PROMPT ENGINEERING
        # We limit the text to the first 2500 characters to stay within the AI's
        # context window and improve processing speed on the product Link
        prompt = f"""
            Extract the following product details from the text below into a valid JSON format.
            Details: 
            - product_name
            - current_price (as numbers only)
            - currency (the symbol or code)
            - stock_status (true if in stock, false if not)

            If a detail is missing, use null.

            Text:
            {page_text[:2500]}
            """

        try:
            # 5. LOCAL LLM REQUEST (Ollama API)
            # Sending the data to your local GPU-accelerated Llama 3 instance
            response = requests.post('http://localhost:11434/api/generate', json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,  # We want the full response at once
                "format": "json"  # Instructs Ollama to return a JSON object
            })

            # 6. PARSING AI RESPONSE
            raw_result = response.json().get('response')
            return json.loads(raw_result)

        except Exception as e:
            print(f"Error analyzing product details: {e}")
            return None


async def main():
    """
    Test script to verify the extraction logic on a single KSP product.
    """
    # Example GPU link
    test_link = "https://ksp.co.il/web/item/369203"

    # Execute the extraction
    product_data = await extract_product_information(test_link)

    # Output the structured data for verification
    print("\n------- Structured Product Data (JSON) ------")
    if product_data:
        print(json.dumps(product_data, indent=4, ensure_ascii=False))
    else:
        print("Failed to extract data.")


if __name__ == "__main__":
    # Start the event loop
    asyncio.run(main())