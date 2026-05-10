# Weather MCP Israel

שרת MCP לשליפת תחזית מזג האוויר בישראל באמצעות אוטומציה של דפדפן עם Playwright.

## תיאור הפרויקט

בפרויקט זה פותח שרת MCP (Model Context Protocol) המאפשר ל־LLM לקבל מידע על מזג האוויר בישראל.

בניגוד לשימוש ב־API ייעודי, הפרויקט מבצע את הפעולות הבאות:

1. פותח דפדפן באמצעות Playwright.
2. ניגש לאתר https://www.weather2day.co.il.
3. מזין שם של עיר בישראל.
4. בוחר את העיר מתוך רשימת ההשלמה האוטומטית.
5. מחלץ את נתוני התחזית מהדף.
6. מחזיר את המידע ל־LLM לצורך ניסוח תשובה מלאה.

## מטרות לימודיות

הפרויקט מדגים:

- פיתוח שרת MCP עצמאי.
- חשיפת Tools ל־LLM.
- שליטה בדפדפן באמצעות Playwright.
- חילוץ מידע מאתר אינטרנט.
- שימוש ב־RAG להעשרת הקונטקסט של המודל.

## טכנולוגיות

- Python
- MCP SDK (`FastMCP`)
- Playwright
- OpenAI API
- uv

## מבנה הפרויקט

```text
project-template/
├── client.py          # לקוח MCP כללי
├── host.py            # Host המחבר בין ה-LLM לשרתי MCP
├── weather_USA.py     # שרת MCP לדוגמה עבור ארה"ב
├── weather_Israel.py  # שרת MCP שפותח במסגרת הפרויקט
├── pyproject.toml
├── .env
└── README.md
הכלים (Tools) שמומשו
open_weather_forecast_israel

פותח את אתר מזג האוויר בישראל.

enter_weather_forecast_city_israel(city_name)

מזין את שם העיר בשדה החיפוש.

select_weather_forecast_city_israel()

בוחר את העיר הראשונה מרשימת ההשלמה.

get_weather_data_israel()

מחלץ את נתוני מזג האוויר מהדף ומחזיר אותם ל־LLM.

הוראות התקנה
התקנת התלויות
uv sync
התקנת הדפדפן של Playwright
uv run playwright install chromium
יצירת קובץ .env
OPENAI_API_KEY=your_openai_api_key
הרצת הפרויקט
uv run host.py
דוגמאות לשאלות
מה מזג האוויר בירושלים?
מה הטמפרטורה כרגע בתל אביב?
מה מזג האוויר בבני ברק?
מה התחזית בחיפה?
אופן הפעולה

כאשר המשתמש שואל:

מה מזג האוויר בבני ברק?

ה־LLM מפעיל את הכלים הבאים לפי הסדר:

open_weather_forecast_israel
enter_weather_forecast_city_israel("בני ברק")
select_weather_forecast_city_israel()
get_weather_data_israel()

לאחר מכן ה־LLM מקבל את המידע שנשלף מהאתר ומחזיר תשובה בשפה טבעית.

דוגמה לפלט
טמפרטורה נוכחית: 23°
לחות: 50%
רוח: 6 קמ"ש
זריחה: 05:48
שקיעה: 19:28
תוצרים לימודיים

במהלך הפרויקט נרכשו היכולות הבאות:

בניית שרת MCP.
חיבור Tools ל־LLM.
אוטומציה של דפדפן.
חילוץ מידע מאתר אינטרנט.
שימוש במידע שנשלף לצורך מענה חכם.