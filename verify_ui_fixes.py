
import asyncio
from playwright.async_api import async_playwright

async def verify_ui_fixes():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Open App
        print("Navigating to app...")
        await page.goto("http://localhost:5173")
        await page.wait_for_selector("text=OCR Demo")
        
        # 2. Verify Confirmation Dialog
        print("Testing Fetch Dialog...")
        await page.click("text=Fetch 100 Internet Samples")
        
        # Check for dialog title
        try:
            await page.wait_for_selector("text=Download 100 Samples?", timeout=2000)
            print("✅ Confirmation Dialog appeared.")
        except:
            print("❌ Confirmation Dialog NOT found.")
            await browser.close()
            return

        # Click Cancel (don't actually fetch 100 again to save time)
        await page.click("text=Cancel")
        
        # 3. Verify Confidence Score
        print("Testing OCR Confidence...")
        # Select first sample (should exist if server running)
        await page.click("text=Letter (handwritten)")
        await page.wait_for_timeout(1000)
        
        # Run OCR
        await page.click("text=Run OCR Extraction")
        
        # Wait for result
        try:
            await page.wait_for_selector("text=Confidence:", timeout=20000)
            content = await page.content()
            if "Confidence: " in content and "%" in content:
                 print("✅ Confidence Score displayed.")
            else:
                 print("❌ Confidence element found but text missing.")
        except Exception as e:
            print(f"❌ Confidence Score NOT found: {e}")

        # 4. Verify "Search Knowledge Base" (Negative Check)
        # Should NOT exist
        if "Search Knowledge Base" in await page.content():
            print("❓ 'Search Knowledge Base' string found in DOM (Unexpected).")
        else:
            print("✅ 'Search Knowledge Base' correctly NOT found in static DOM.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_ui_fixes())
