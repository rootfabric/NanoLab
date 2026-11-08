#!/bin/bash
# SOURCE-75 R1 — Nanobase 256 (Narcissus) / 257 (Echo) retrieval script.
# Официальный источник: api.nanobase.org (дизайн-файлы) + nanobase.org (альтернативный маршрут).
# Правила: C0 (без научных вычислений), лимит 256 MiB, только официальные поверхности,
# каждый файл: URL -> HTTP -> байты -> SHA-256 -> SHA-1. Никаких платных сервисов.
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
DL="$ROOT/downloads"
LOG="$ROOT/logs"
mkdir -p "$DL" "$LOG"
UA="NanoLab-SOURCE-75-provenance/1.0 (research provenance receipt; repo issue #75)"
BUDGET_BYTES=$((256*1024*1024))
MANIFEST="$LOG/download_receipts.tsv"
[ -f "$MANIFEST" ] || printf 'ts\tname\turl\thttp\tcontent_type\tbytes\tsha256\tsha1\n' > "$MANIFEST"

total_bytes=0
fetch () {
  local name="$1" url="$2"
  local ts hdr body code ctype size
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  hdr="$LOG/hdr_${name}.txt"; body="$DL/${name}"
  code=$(curl -sS --max-time 180 -A "$UA" -L --max-redirs 5 \
        -o "$body" -D "$hdr" \
        -w '%{http_code}\t%{content_type}\t%{size_download}\t%{url_effective}' "$url")
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo -e "$ts\t$name\t$url\tCURL_ERR_$rc\t-\t0\t-\t-" >> "$MANIFEST"
    rm -f "$body"; return 1
  fi
  code_http=$(printf '%s' "$code" | cut -f1)
  ctype=$(printf '%s' "$code" | cut -f2)
  size=$(printf '%s' "$code" | cut -f3)
  final_url=$(printf '%s' "$code" | cut -f4)
  if [ "$code_http" != "200" ]; then
    echo -e "$ts\t$name\t$url\tHTTP_$code_http\t$ctype\t$size\t-\t-" >> "$MANIFEST"
    rm -f "$body"; return 1
  fi
  local s256 s1
  s256=$(sha256sum "$body" | cut -d' ' -f1)
  s1=$(sha1sum "$body" | cut -d' ' -f1)
  total_bytes=$((total_bytes + size))
  echo -e "$ts\t$name\t$final_url\t$code_http\t$ctype\t$size\t$s256\t$s1" >> "$MANIFEST"
  echo "OK  $name $size B sha256=$s256"
  # бюджет: стоп при превышении 256 MiB суммарной передачи
  if [ "$total_bytes" -gt "$BUDGET_BYTES" ]; then echo "BUDGET EXCEEDED, abort"; exit 2; fi
}

API="https://api.nanobase.org"
SITE="https://nanobase.org"

# 1) живые листинги (метаданные)
fetch listing_256.json        "$API/api/v1/structure/structure-files?id=256"
fetch listing_257.json        "$API/api/v1/structure/structure-files?id=257"
fetch listing_256_getox.json  "$API/api/v1/structure/getStructureOxdnaFiles?id=256"
fetch listing_257_getox.json  "$API/api/v1/structure/getStructureOxdnaFiles?id=257"
fetch catalog_all.json        "$API/api/v1/structure/getAllPublicStructures_paginated?skip=0&take=120"

# 2) дизайн-файлы записи 256 (Narcissus) — листинг от 2026-10-18 (nb_files_256.json, sha256 d086416e…)
fetch 256_N.oxview                     "$API/api/v1/structure/files/256/structure/N.oxview"
fetch 256_N_nanobase.json              "$API/api/v1/structure/files/256/structure/N_nanobase.json"
fetch 256_Narcissus_staples_p7560.xlsx "$API/api/v1/structure/files/256/structure/Narcissus%20staples%20p7560.xlsx"

# 3) дизайн-файлы записи 257 (Echo) — листинг от 2026-10-18 (nb_files_257.json, sha256 c5d037a9…)
fetch 257_E.oxview                     "$API/api/v1/structure/files/257/structure/E.oxview"
fetch 257_E_nanobase.json              "$API/api/v1/structure/files/257/structure/E_nanobase.json"
fetch 257_Echo_staples_p7560.xlsx      "$API/api/v1/structure/files/257/structure/Echo%20staples%20p7560.xlsx"

# 4) альтернативный маршрут основного сайта (GitHub sulcgroup/nanobase main.py: /file/<id>/<type>/<file>)
[ -f "$DL/256_N.oxview" ] || fetch 256_N.oxview_via_site "$SITE/file/256/structure/N.oxview"
[ -f "$DL/257_E.oxview" ] || fetch 257_E.oxview_via_site "$SITE/file/257/structure/E.oxview"

echo "---- summary ----"
column -t -s $'\t' "$MANIFEST" || cat "$MANIFEST"
