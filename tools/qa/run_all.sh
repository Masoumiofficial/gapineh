#!/usr/bin/env bash
# اجرای همهٔ تست‌های QA صفحهٔ فروش گپینه.
# نیازمندی: Python 3 (html5lib, tinycss2) و Node.js 18+ با jsdom.
#   PYTHON=/path/to/venv/bin/python bash tools/qa/run_all.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "== QA استاتیک =="
${PYTHON:-python3} tools/qa/check_static.py

if [ -d node_modules/jsdom ]; then
  echo
  echo "== QA رفتاری (jsdom) =="
  node tools/qa/test_dom.mjs
else
  echo
  echo "جستنشده: jsdom نصب نیست."
  echo "برای اجرای تست رفتاری:  npm install --no-save jsdom  سپس دوباره اجرا کنید."
fi
