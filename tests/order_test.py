#!/usr/bin/env python3
"""One TEST order against a deployed preview. Honors the 5-orders-per-hour limit.

Do not loop this script. A 429 is reported and not retried.
The parent runs it after deploying mapot-preview. This environment does not deploy.

  python3 tests/order_test.py
  python3 tests/order_test.py https://mapot-preview.hayahara-site.pages.dev
"""
import json, sys, urllib.error, urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://mapot-preview.hayahara-site.pages.dev").rstrip("/")
ORDER = {
    "business": "בדיקת תצוגה",
    "contact": "בדיקה",
    "phone": "053-2535393",
    "email": "office@hayahara.co.il",
    "event_date": "2026-12-01",
    "address": "פרי גן 16 מישור אדומים",
    "notes": "TEST בדיקת זרימה מהסקריפט",
    "items": [
        {"sku": "TC-LINEN-3X3", "color": "c01", "qty": 2},
        {"sku": "CC-STD", "color": "", "qty": 4},
    ],
}
req = urllib.request.Request(
    BASE + "/mapot/api/order",
    data=json.dumps(ORDER).encode(),
    headers={"content-type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as res:
        body = json.loads(res.read().decode())
        print(res.status, json.dumps(body, ensure_ascii=False))
        if not body.get("ok"):
            sys.exit(1)
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())
    sys.exit(1)
