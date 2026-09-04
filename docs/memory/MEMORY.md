# 專案長期備忘 (AI Test / 流動日報)

## 下次先讀（省 token）
- 線上頁：**https://liuchiwai0101.github.io/News/**（大寫 `News`）。`/news/` 會 404（GitHub Pages 區分大小寫；倉庫已改名 `News`）。
- 本倉是 GitHub Pages **產出**（`index.html` / `articles.js` / `articles/`）。`nml-daily.html` 只做轉址到 `/#nml`，不再單獨報表。構建腳本在本機 `.workbuddy/tmp/build_dashboard.py`，**不在此 repo**。改前端必須改模板，否則隔日 07:00 / 13:00 rebuild 會蓋掉。
- **`build_nml_report.py` 已廢棄**：不要再跑、不要再產青綠獨立頁。其僅有的獨特 bits 已抄進 `build_dashboard.py`（見下方「抄入 bits」）。`run_daily.cmd` / `run_daily.py` 刪掉對它的呼叫。
- 不要重掃全站、不要加額外功能／測試檔／chat-history。前端已知小 bug（應改**Windows 模板**，Pages 上的 PR #2 不夠）：JS 重建 nav 時漏色點；搜尋空結果不要用 `[style*="display: none"]`；手機 CSS 要包含 `.nav-inner-old`。在線 Worker 仍是佔位，已有 herenow 回退，不必再加一層。
- **排程（2026-09-04）**：Windows `AIReviewDailySite` 自 08-26 後不再直推 main；Cursor 日更 agent `bc-01a045b3` IDLE、開 PR 不 merge 就不發佈。**真正會更新網站的是 GitHub Actions** `.github/workflows/daily.yml`（每日兩次：北京 07:00 = 23:00 UTC、北京 13:00 = 05:00 UTC，`workflow_dispatch` 可手動），跑 `scripts/rebuild_daily.py` 後 **直接 commit push `main`** → Pages。不要再開只停在 PR 的日更。GitHub 公開倉 cron 常會晚幾小時。
- **預覽**：只在瀏覽器打開頁面即可。不要截圖、不要產出 walkthrough 圖片／影片。

## 自動化
- **現行發佈路徑**：GitHub Actions `Daily dashboard`（cron 北京 07:00 與 13:00，或 Actions 頁手動 Run）→ `scripts/rebuild_daily.py` → push `main` → `pages-build-deployment`。Windows `AIReviewDailySite` 與 Cursor 日更 PR **不再依賴**。
- 舊 Cursor 任務名 **automation-1784089722231** 不是 UUID；`list-cloud-agents(sources=["automations"])` = 0。
  流程：fetch_daily → scrape_nml → build_dashboard(1) → 中文/前端補充 → build_dashboard(2) → pin 置頂 → cp→ghpages→git push → WeChat。**不要再跑 `build_nml_report.py`**（已 drop；bits 抄入 `build_dashboard.py`；`nml-daily.html` 由 dashboard 寫成 `/#nml` 轉址）。
- 發佈目標：GitHub Pages 倉庫在 `ghpages/`（remote 含 x-access-token，勿外洩）。固定網址 **https://liuchiwai0101.github.io/News/**（勿用小寫 `/news/`）。
- **git push 至 ghpages 必須先禁 GCM**：`ghpages` 倉庫若帶 `credential.helper=manager`（Git Credential Manager），非互動 shell 下 push 會卡死（read/ls-remote 正常，write/push 懸停數十分鐘）。**修正**：`git -C ghpages config --local credential.helper ""`（token 已內嵌 URL，毋須 GCM）。禁用後 push 秒完成（如 `af39846..98323bd`）。另：`protocol.version=0` + `http.version=HTTP/1.1` 可繞過偶發的 `expected flush after ref listing` v2 協商錯誤（read 慢但不影響 write）。

## 限時情报王 監測慣例（避免誤報的關鍵）
- `scrape_nml.py` 爬雙分類：限時情报王 + 限時免費情報，寫 `nml_snapshot.json`（聯集）。
- **`nml_new.json` = 本輪真正新增的 url 集合（authoritative NEW 來源）**，由 scrape_nml.py 在更新 nml_seen.json「之前」寫出。
- `build_dashboard.py` 的 load_nml_section：優先讀 nml_snapshot.json（雙分類），NEW 標記讀 nml_new.json（**不要用 nml_seen 比對，否則全站誤報**），並 insert(0) 把限時情报王 放最前（NML_MAX=40）。
- 儀表盤 `const NML = {total, shown, newCount}`（從 snapshot 全長、NML_MAX、nml_new 算出）顯示在 hero「新增 · 顯示 N / 全站 M」、限時情報王 panel（含「監測分類：限時情報王 ＋ 限時免費情報」）、footer；`#nml` 會打開該板塊。
- **抄入 bits**（從已 drop 的 `build_nml_report.py` 抄進 `build_dashboard.py`，然後刪掉該檔）：
  1. `NML = {total: len(snapshot), shown: min(NML_MAX, len(items)), newCount: len(nml_new)}`，寫入 index 的 `const NML = {...};`（緊接 `const DATA = ...`）。
  2. 寫 `nml-daily.html` 為轉址頁（不要再產青綠卡片牆）：`<meta http-equiv="refresh" content="0; url=./#nml">` + `location.replace('./#nml')`。
  3. 模板 JS：hero 一顆 pill「新增 · 顯示 / 全站」；external panel `cnt` 用「顯示 · 全站 · 新增」+ `.nml-sub` 監測分類；footer 全站/本頁/新增；`openNmlHash()` 認 `#nml`。
  4. `run_daily` 刪掉 `python build_nml_report.py` 那一步。
- `pin_nml_top.py` 為冪等安全網（build 已置頂則不變動）。
- 若 newmobilelife.com 改版擷取失敗，build 回退本地 snapshot，不誤報。

## 網站前端功能
- **在線人數（按 IP 統計）**：`build_dashboard.py` 模板內已內建「實時在線 N 人」徽章（脈動綠點 + 數字）。
  位置：**右下角浮動徽章**（`position:fixed; right:16px; bottom:16px; z-index:60;`）。底色 `rgba(27,38,107,.85)`（只留儀表盤一顆；nml 獨立頁已 drop）。
  實作：**自建 Cloudflare Worker**（`online-counter/worker.js` + `wrangler.toml` + `README.md`）。前端每 60s 打 `/heartbeat`、每 30s 打 `/online`；Worker 取 `CF-Connecting-IP` 寫入 Workers KV（key=IP, TTL 90s），`/online` 統計 60s 視窗內不同 IP 數 = 當前在線人數（同一 IP 多開只算 1）。
  **尚未部署 → 已加回退**：`build_dashboard.py` 內 `WORKER` 常數目前為佔位 `https://news-online-ip.<your-subdomain>.workers.dev`。為避免「徽章看不到」，已加 **herenow 回退**：先試 Worker `/online`；若 fetch 失敗（佔位網址不可達）則改打 `https://herenow-anhz7w.fly.dev` 的 `/ping`（帶 sessionId）+ `/count?page=...`，用連線數即時顯示「實時在線 N 人」（N 最小顯示 1）。Worker 部署完成、回填真實 subdomain 後即自動升級為「按 IP 去重」真計數，無需改程式碼。
  優點（Worker 模式）：IP 只存使用者自己的 KV、60s 自動過期，不落第三方、免費免信用卡；每日 rebuild 會自動保留（已進模板）。回退模式依賴第三方 herenow 免費服務，掛掉時徽章隱藏（graceful degrade）。

## 舊聞（Old News）板塊歸類
- `build_dashboard.py` 的 `renderOld`（舊聞分頁，`view-old`）**按原板塊分組**：每個板塊一個 `panel-head`（色條+標題+條數）+ `grid wall`，順序跟隨 `DATA.sections` 當前順序。
- **舊聞分組導航（2026-08-13 新增）**：`view-old` 內新增 `<nav class="nav nav-old"><div class="nav-inner-old">`，由 `renderOld` 動態填入「全部」+ 各板塊 `.nav-link`（帶即時條數），**與最新版面 group 導航 UX 一致**。點擊板塊連結僅顯示該 `old-panel`（`data-cat=板塊名`），「全部」顯示全部。`nav-inner-old` 共用 `.nav-inner` 的 CSS；舊面板 class 改為 `section old-panel` + `data-cat`。
- **重要**：主版面 nav 點擊處理器已 scoping 至 `#view-current`（原 `document.querySelectorAll('.nav-link'/.tab-panel')` 會誤傷舊聞面板），舊聞 nav 處理器 scoping 至 `.nav-inner-old` / `#view-old .old-panel`，兩者互不干擾。
- 實作關鍵：歸檔時記錄原板塊。`_url_board` 由 `sections_out` 建立 url→label 映射，寫入 `_archive[_u]["board"]`；`renderOld` 依 `it.board` 分組（缺省→「其他」）。
- 歷史 backfill：舊 archive 條目無 board，依 `kind` 推斷（external→限時情報王、deals→熱門優惠；aihot 留空→「其他」）。新歸檔條目自帶精確 7 板塊，「其他」隨時間減少。
- **驗證方式**：用 jsdom（node workspace 已裝）載入 build_site/index.html，切到舊聞 tab，模擬點擊 nav 驗證篩選；archived 0 條時 nav 清空（early return）。

## Python 環境
- 構建/擷取（需 trafilatura/opencc）：`C:/Users/vincentliu/.workbuddy/binaries/python/envs/default/Scripts/python`
- 爬蟲/報表/置頂（純 stdlib）：`C:/Users/vincentliu/.workbuddy/binaries/python/versions/3.13.12/python.exe`
- 關鍵腳本皆在 `.workbuddy/tmp/`：fetch_daily.py / scrape_nml.py / build_dashboard.py / fetch_supplement.py / pin_nml_top.py。（`build_nml_report.py` 已 drop，bits 抄入 `build_dashboard.py`。）
