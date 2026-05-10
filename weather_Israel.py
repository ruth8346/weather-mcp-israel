import asyncio
import re

from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("weather-Israel")

state = {
    "playwright": None,
    "browser": None,
    "page": None,
}


async def get_page():
    if state["page"] is None:
        raise RuntimeError("יש להפעיל קודם את open_weather_forecast_israel")
    return state["page"]


@mcp.tool()
async def open_weather_forecast_israel() -> str:
    """פותח את אתר התחזית של ישראל בדפדפן."""
    if state["playwright"] is None:
        state["playwright"] = await async_playwright().start()
        state["browser"] = await state["playwright"].chromium.launch(
            headless=False,
            slow_mo=300
        )
        state["page"] = await state["browser"].new_page(
            viewport={"width": 1400, "height": 900}
        )

    page = state["page"]

    await page.goto(
        "https://www.weather2day.co.il/forecast",
        wait_until="domcontentloaded",
        timeout=60000
    )

    await asyncio.sleep(2)

    # סגירת הודעת עוגיות בלי למחוק אלמנטים מהדף
    try:
        await page.get_by_text("מקובל").click(timeout=3000)
    except Exception:
        pass

    await asyncio.sleep(1)

    return "האתר נפתח בהצלחה."


@mcp.tool()
async def enter_weather_forecast_city_israel(city_name: str) -> str:
    """מזין שם עיר בשדה החיפוש באתר."""
    page = await get_page()

    inputs = page.locator("input")

    count = await inputs.count()
    chosen_input = None

    for i in range(count):
        current = inputs.nth(i)
        try:
            if await current.is_visible():
                box = await current.bounding_box()
                if box and box["width"] > 250:
                    chosen_input = current
                    break
        except Exception:
            continue

    if chosen_input is None:
        raise RuntimeError("לא נמצא שדה חיפוש גלוי בדף.")

    await chosen_input.click()
    await chosen_input.fill("")
    await chosen_input.press_sequentially(city_name, delay=120)

    await asyncio.sleep(3)

    return f"העיר {city_name} הוקלדה בשדה החיפוש."


@mcp.tool()
async def select_weather_forecast_city_israel() -> str:
    """בוחר את העיר הראשונה מהרשימה הנפתחת."""
    page = await get_page()

    await page.keyboard.press("ArrowDown")
    await asyncio.sleep(1)
    await page.keyboard.press("Enter")

    await page.wait_for_load_state("domcontentloaded")
    await asyncio.sleep(3)

    return "העיר הראשונה נבחרה מהרשימה."


@mcp.tool()
async def get_weather_data_israel() -> str:
    """מחלץ מידע מהדף הנוכחי ומחזיר אותו ל-LLM."""
    page = await get_page()

    text = await page.locator("body").inner_text()

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    clean_text = "\n".join(lines)

    temp_match = re.search(r"(-?\d+(?:\.\d+)?)\s*°", clean_text)

    if temp_match:
        return (
            f"המידע חולץ בהצלחה.\n"
            f"טמפרטורה שנמצאה בדף: {temp_match.group(1)}°\n\n"
            f"תוכן רלוונטי מהדף:\n{clean_text[:4000]}"
        )

    return f"המידע חולץ מהדף, אך לא נמצאה טמפרטורה ברורה:\n{clean_text[:4000]}"


if __name__ == "__main__":
    mcp.run(transport="stdio")