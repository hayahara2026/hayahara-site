# אתר מכבסת היערה — hayahara.co.il

אתר סטטי (HTML) של מכבסת היערה, מכבסה תעשייתית לעסקים ולמוסדות מאז 1980. כתובת המכבסה: פרי גן 16, מישור אדומים.

## אירוח
- האתר מתפרסם ב־GitHub Pages מהענף `main`, תיקיית השורש (`/`).
- דומיין: https://hayahara.co.il (קובץ `CNAME` בשורש, Custom domain ב־Settings → Pages, ‏Enforce HTTPS). ‏www מפנה לדומיין הראשי.
- DNS ב־Cloudflare: ארבע רשומות A לכתובות של GitHub Pages ו־CNAME ל־`www` אל `hayahara2026.github.io`, במצב DNS only (ענן אפור).
- הכתובת הישנה https://hayahara2026.github.io/hayahara-site/ מפנה אוטומטית לדומיין. לא למחוק את קובץ `CNAME`.
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
- רק נתיבים יחסיים (`assets/...`, `./`; בתוך `services/`: `../assets/...`, `../`). בלי `/assets` ובלי `href="/"`, כי ב־github.io האתר יושב בתת־תיקייה.
- canonical, ‏og:url, ‏sitemap ו־llms.txt תמיד עם `https://hayahara.co.il/`.
- כל עמוד חדש: להוסיף ל־`sitemap.xml` ול־`llms.txt`.
- קבצים פנימיים (`AUDIT_HE.md`, `GIL_DOMAIN_HE.md`) לא נכנסים לריפו (ראו `.gitignore`).
