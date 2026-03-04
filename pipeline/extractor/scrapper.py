from playwright.async_api import async_playwright
from utils.logger import logger

_playwright = None
_browser = None
_context = None


async def get_browser():
    global _playwright, _browser
    if _browser is None:
        logger.info("Launching browser")
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
    return _browser


async def get_context():
    global _context
    if _context is None:
        logger.info("Creating browser context")
        browser = await get_browser()
        _context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    return _context


async def page_scrapper(url: str, *args) -> dict:
    target_url = url.format(*args)
    logger.info(f"Scraping: {target_url}")
    context = await get_context()
    page = await context.new_page()
    result = {}

    async def handle_response(response):
        if target_url not in response.url:
            return
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return
        try:
            data = await response.json()
            if isinstance(data, dict):
                result.update(data)
            else:
                result["data"] = data
            logger.info(f"Got JSON from: {response.url}")
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")

    page.on("response", handle_response)
    await page.goto(target_url, wait_until="networkidle")
    await page.close()
    return result


async def close_browser():
    global _playwright, _browser, _context
    if _context:
        await _context.close()
        _context = None
    if _browser:
        await _browser.close()
        await _playwright.stop()
        _browser = None
        logger.info("Browser closed")