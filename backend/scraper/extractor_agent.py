import asyncio
import requests
import json
from playwright.async_api import async_playwright

async def extract_product_information(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"scaning product: {url}")
        await page.goto(url,wait_until='networkidle')

        #extract raw text from the page
        page_text = await page.inner_text("body")
        await browser.close()

        print("Analyze product using AI....")
        prompt = f"""
            Extract the following product details from the text bellow into a valid JSON format.
            Details: product_name , current_price(as a numbers only),currency(which currency is used) ,and stock_status(true/false) 
            if you cant find a detail, use null/
            
            Text:
            {page_text[:2500]}
            """
        try:
            response = requests.post('http://localhost:11434/api/generate',json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            })

            #extract AI answer Resposne
            raw_result = response.json().get('response')
            return json.loads(raw_result)
        except Exception as e:
            print(f"error in analyze product details: {e}")
            return None

async def main():
    test_link = "https://ksp.co.il/web/item/369203"
    product_data = await extract_product_information(test_link)

    print("\n------- The details extracted from the text bellow into a valid JSON format ------")
    print(json.dumps(product_data, indent=4,ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())