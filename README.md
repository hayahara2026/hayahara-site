# אתר מכבסת היערה — hayahara.co.il

אתר סטטי (HTML) של מכבסת היערה, מכבסה תעשייתית לעסקים ולמוסדות מאז 1980, פרי גן 16, מישור אדומים.

## אירוח
- האתר מתפרסם ב־GitHub Pages מהענף `main`, תיקיית השורש (`/`).
- כתובת זמנית: https://hayahara2026.github.io/hayahara-site/
- הדומיין `hayahara.co.il` יחובר רק אחרי שרשומות ה־DNS יעבדו. **לא להוסיף קובץ `CNAME` ולא להגדיר Custom domain לפני כן.**
- ‏`.nojekyll` נשאר בשורש, כדי ש־GitHub יגיש את הקבצים כמו שהם.

## מבנה
- `index.html`: דף הבית
- `about.html`, `contact.html` (מפה בטעינה בלחיצה), `faq.html`
- `services/`: עמוד שירותים, 6 עמודי שירות ו־4 עמודי קהל (slugs קבועים, לא לשנות)
- `privacy.html`, `accessibility.html`, `terms.html`: עמודים משפטיים
- `404.html`: עמוד שגיאה עצמאי (CSS מוטמע, קישורים מלאים ל־https://hayahara.co.il/)
- `assets/css/site.css`, `assets/js/site.js`: עיצוב וסקריפט משותפים
- `assets/`: לוגו, תמונות, `og-image.jpg` ו־`icons/`
- `favicon.ico`, `site.webmanifest`, `robots.txt`, `sitemap.xml`, `llms.txt`

## כללים
- נתיבים יחסיים בלבד (`assets/...`, `./`; בתוך `services/`: `../assets/...`, `../`). בלי `/assets` ובלי `href="/"`, כי ב־github.io האתר יושב בתת־תיקייה.
- canonical, ‏og:url, ‏sitemap ו־llms.txt תמיד עם `https://hayahara.co.il/`.
- כל עמוד חדש: להוסיף ל־`sitemap.xml` ול־`llms.txt`.
- קבצים פנימיים (`AUDIT_HE.md`, `GIL_DOMAIN_HE.md`) לא נכנסים לריפו (ראו `.gitignore`).
