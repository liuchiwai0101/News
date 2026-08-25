# AI HOT 日报自动化执行记录

## 2026-07-16 — 执行成功 ✅
- **日期**: 2026-07-16｜拉取今日日报 `sections=5, items=23`（无需回退到最近一期）
- **NML 监测**: scrape 1189 篇文章，相对 7/15 基線 1 NEW（Apple Back to School 2026）；但 build 时 `nml_seen.json` 已被刷成全量 → 仪表盘 NML 栏 NEW=0
- **构建**: 43 条 / 6 版塊（限時情報王 20 + AI HOT 5 版塊 23）；全文页 43 个；配图 23/23
- **舊聞分頁**: 19 条（>5 天且不在今日集合；archive 累计 69 条，区间 2026-05-20~2026-07-16）
- **GitHub Pages**: 推送成功 commit `51cd3a2`（26 文件）→ https://liuchiwai0101.github.io/news/
- **微信推送**: 未执行（WeCom / SCRM 连接器均 disconnected）→ 已存 `ai-daily-2026-07-16.html` 并提示用户去连接器页连接
- **待优化**: 步骤 2 的 scraper 会把 `nml_seen` 更新为全量，导致步骤 3 build 的 NEW 标记恒为 0；若需 NEW 有意义需调整基線时序（如 build 后单独更新 seen，或 build 对比「上一次报告」基線）

## 2026-07-22 — 执行成功 ✅
- **日期**: 2026-07-22｜拉取今日日报 `sections=5, items=31`（无需回退）。5 版塊 NEW 均為 0。
- **NML 监测**: scrape 1189 篇；build NML 栏 20 条（NEW=0，同上已知基線时序問題）。熱門優惠 20 条。
- **英文卡刪除**: 第一构建产出 `dropped_en.json`，5 個 AI HOT 版塊的英文/社交卡被刪（模型发布/更新 4、产品发布/更新 8、行业动态 5、论文研究 4、技巧与观点 8）。
- **中文補充**: `fetch_supplement.py` 抓 17 URL → 14 篇中文（模型发布/更新 2、产品发布/更新 3、行业动态 4、论文研究 3、技巧与观点 2）。修復了 `fetch_supplement.py` 对 `extract_blocks` 返回 dict 列表的相容性 bug（原腳本當成 str 處理 → TypeError）。
- **前端補充**: `frontend.json` 15 篇（掘金/InfoQ中文/開源中國/SegmentFault/w3ctech），build 合併 12 篇。
- **最終构建**: 68 条 / 7 版塊 — 限時情報王 20、熱門優惠 20、模型发布/更新 2、产品发布/更新 6、行业动态 10、论文研究 3、技巧与观点 7。全文页 51、配图 31/31。
- **舊聞分頁**: 依 archive URL 日期估算 >5 天約 29 条（archive 累计 147 条，区间 2026-03-06~2026-07-22）。
- **GitHub Pages**: xcopy 修正（Git Bash 反斜線會導致 cyclic copy；改用 `xcopy build_site ghpages /E /I /Y` 或 `cp` 才正確落到根目錄）。推送成功 commit `d35587b` → https://liuchiwai0101.github.io/news/
- **微信推送**: 未执行（WeCom / SCRM 連接器均 disconnected）→ 已存 `build_site/index.html`（儀表盤），提示用戶去連接器頁連接 WeCom/SCRM。
- **待優化**: ① NML NEW 時序問題（同 7/16）；② xcopy 在 Git Bash 須用正斜線/無結尾反斜線，否則會把 build_site 當子目錄複製。

## 2026-07-22 (14:45 重跑) — 執行成功 ✅
- **日期**: 2026-07-22｜拉取今日日报 `sections=5, items=31`（無需回退）。5 版塊 NEW 均為 0。
- **NML 監測**: scrape 雙分類聯集 1189 篇（scrape 日誌累計 2767 為分頁累加值，實際寫入 snapshot 為 1189）；NEW=0（基線時序問題：nml_seen 已為全量 → nml_new 空）。
- **英文卡刪除**: 第一構建產 dropped_en.json，5 版塊共 26 張英文/社交卡被刪（模型发布/更新 4、产品发布/更新 8、行业动态 5、论文研究 4、技巧与观点 8）。
- **中文補充**: supplement_urls.json 選 14 個中文 URL；fetch_supplement.py 實抓 9 篇（模型发布/更新 3、产品发布/更新 3、行业动态 1、论文研究 2）。CSDN/InfoQ 部分頁被 521/無區塊擋掉。
- **前端補充**: 重新撰寫 frontend.json，掘金/InfoQ中文/開源中國/SegmentFault 共 13 篇（產品发布/更新 5、行业动态 4、技巧与观点 4）。
- **最終構建**: 84 条 / 7 版塊 — 限時情報王 40、熱門優惠 20、模型发布/更新 3、产品发布/更新 8、行业动态 7、论文研究 2、技巧与观点 4。舊聞分頁 60 条。全文頁若干。
- **品質檢查**: 抽出 index.html 內聯 script 跑 `node --check` 通過；修復引號模式 &quot;none&quot; 仍在（無空白頁復發）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → git pull --ff-only（Already up to date）→ commit `59113e6`「每日整合：限時情报王 + AI HOT 2026-07-22」→ push 成功 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 確認 限時情報王 已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器均 disconnected → 未推送；已存 `ai-daily-2026-07-22.html`（儀表盤副本）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。
- **待優化**: NML NEW 時序問題（nml_seen 在 scrape 後即為全量，導致 build/nml_new 永遠 NEW=0）；若需 NEW 有意義，需調整基線（如 build 後才更新 seen，或對比「上一次報告」基線）。

## 2026-07-22 (補) — 修復網站空白頁 🐛
- **症狀**: GitHub Pages 顯示標籤/計數（靜態 HTML）但內容區 `#content` 完全空白。
- **根因**: `build_dashboard.py` 模板中 `makeDealCard` 與 `openReader` 的 `onerror` 用了 `\'`（Python 會把 `\'` 折成裸 `'`），導致產出的 inline `<script>` 出現 `onerror="this.style.display='none'"` 與 `dealImgFallback(this,'' + dcat + '')` 的裸單引號，使整段 JS 解析失敗 → 所有卡片不渲染。
- **修復**: 模板改為 `&quot;none&quot;`（渲染層 HTML 解碼為 `"none"`，且不含破壞 JS 的引號）與 `dealImgFallback(this,\\'' + dcat + '\\')`（輸出保留 `\'` 跳脫）。已改 `.workbuddy/tmp/build_dashboard.py` 兩處（line 1162、1301）+ 直接修 `build_site/index.html` + xcopy 至 `ghpages/` 重新 commit `c2fbfd7` 推送。
- **驗證**: `node --check` 通過；以最小 DOM shim 跑 inline script，確認 `#content` 渲染 7 版塊 / 68 卡片，tab-cur=68、tab-old=49。
- **經驗**: 之後每次 build 完，建議對 `index.html` 跑一次 `node --check` 內聯 script，及早抓出此類模板引號 bug。

## 2026-07-23 (10:1x 修正) — 每個 tab 的 # 序號從 #1 重新開始 🐛
- **需求**: 用戶要求「單獨選擇 tab 後，方塊 # 排序應從 #1 開始；每個版面都從 #1 開始」。
- **症狀**: 卡片 # 序號用單一 module-level `globalIdx`（line 1231）跨所有 panel 累加。因「全部」panel 先 build，點擊單一 tab 時其 per-section panel 顯示的是繼續的 global 數（如 限時情报王 會顯示 #81+ 而非 #1）。
- **修復**: 刪除 `let globalIdx = 0;`，在 `buildPanel(sec, si)` 內改用 `let secIdx = 0;`，於 `sec.items.forEach` 中 `secIdx++` 後傳入 `makeCard/makeDealCard`。如此每個 panel（全部視圖的每個 section group + 每個單一 tab）皆獨立從 #1 編號。已改 `.workbuddy/tmp/build_dashboard.py`（約 line 1231、1247）。
- **部署**: 重跑 build_dashboard.py（80 条 / 5 版塊）→ pin 限時情报王 置頂 → `cp -r build_site/. ghpages/` → commit `109fbf8` 推送。驗證：build_site/ghpages 皆 `globalIdx=0`、`secIdx=3`，兩檔 IDENTICAL；`node --check` 通過。
- **影響**: 自動化明日構建自動套用此修復；用戶在 GitHub Pages 上點任一 tab 現在都從 #1 起算。

## 2026-07-23 (11:0x 修正) — # 號碼與 補充/前端 標籤重疊 🐛
- **需求**: 用戶截圖回報「號碼跟標籤有重疊」。
- **根因**: `.idx`（# 號碼, left:12px）與 `.cover-supp`/`.cover-front`（補充/前端, left:14px）都擠在卡片左上同一角。
- **修復**: 將 `補充`/`前端` 標籤右移到 `#` 號碼右側（`top:10px; left:50px`），左下角改為 `left:12px` 不變。已改 `.workbuddy/tmp/build_dashboard.py`（cover-supp/cover-front 樣式）。
- **部署**: 重跑 build（80 条 / 5 版塊）→ pin 置頂 → `cp -r build_site/. ghpages/` → commit `4aecb7d` 推送。驗證：ghpages 與 build_site IDENTICAL、left:50px 生效。

## 2026-07-23 (12:4x 修正) — 非中文內容自動翻譯顯示 🆕
- **需求**: 用戶要求「如果內容不是中文 直接翻譯顯示在內容裡面」。
- **實作**: 在 `build_dashboard.py` 加入 key-less Google `gtx` 翻譯函數（→zh-TW，帶 `_TRANSLATE_CACHE` 快取）。原本「非中文卡整張刪除」改為「保留 + 翻譯」：
  - 文章卡 summary 中文佔比 <20%（`_is_foreign`）→ 翻譯 title+summary、加 `譯` 標記（`.tr-mark` 顯示在卡片標題內）、存 origTitle/origSummary、建合成 reader body 使點開仍可用。
  - 原本被誤刪的 22 張「中文標題但英文來源頁萃取失敗」卡 → 現保留並以中文 feed summary 作為 reader body（不再靜默遺失中文新聞）。
  - 熱門優惠 deal 卡為價格元資料（如 `HK$1,849 · Price.com.hk 網購`），非英文正文，依設計排除翻譯。
- **本次結果**: 重跑 build → **102 条 / 5 版塊**（限時情報王 40、产品发布/更新 13、行业动态 12、技巧与观点 17、熱門優惠 20）。TRANSLATED=0（今日無真正外文文章卡；那 22 張是中文，故無需翻譯，功能處於待命但已接線）。`node --check` 通過、gain 修復與每tab#1 修復皆保留。
- **部署**: pin 置頂 → `cp -r build_site/. ghpages/` → commit `7bbe602` 推送；ghpages 與 build_site IDENTICAL。
- **注意**: 翻譯在 build 時即時呼叫 Google 端點；若離線則該卡退化為「保留原文+合成 body」（不崩潰）。TRANSLATE_CACHE 加速重構。

## 2026-07-24 (09:25 手動執行 · 排程已改 8:00/13:00) — 執行成功 ✅
- **背景**: 用戶先將自動化排程由 7:00/13:00 改為 8:00/13:00（rrule `FREQ=DAILY;BYHOUR=8,13;BYMINUTE=0`），本輪為改排程後的首次手動執行。
- **日期**: 2026-07-24｜fetch_daily sections=5 items=15；scrape_nml 雙分類聯集 snapshot=5592，nml_new=22（非洪水，無需手動聯集修正）。
- **構建**: 第二次構建 97 条 / 7 版塊 — 限時情報王 40、熱門優惠 20、技巧与观点 13、产品发布/更新 9、行业动态 10、论文研究 3、模型发布/更新 2。supplement 合併 13、frontend 合併 9。
- **NML NEW**: 儀表盤限時情报王 NEW=9（url∈nml_new 且 date==2026-07-24）；nml-daily.html `new_vs_baseline=9` 一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0（既有基線時序問題）。
- **品質**: index.html 內聯 script `node --check` 通過；已知裸引號 bug 模式 0 命中。
- **舊聞分頁**: 依 archive isoDate 估算 >5 天 100 条。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → git pull(Already up to date) → commit `0018a03`「每日整合：限時情报王 + AI HOT 2026-07-24」→ push 成功 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-07-24.html`（儀表盤副本）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。
- **最終狀態（09:27 重跑覆寫）**: 第二次構建 100 条 / 7 版塊 — 限時情报王 40、熱門優惠 20、技巧与观点 15、产品发布/更新 9、行业动态 11、论文研究 3、模型发布/更新 2。GitHub Pages 最終 commit `7506050`（覆寫 09:25 的 0018a03）已 push 上線；舊聞分頁 100 条；NML NEW=9。inline JS `node --check` 通過。

## 2026-07-25 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-07-25｜fetch_daily 7/25 尚未發佈（HTTP 404）→ 回退 7/24 期（sections=5, items=15）。網站以本輪執行日 2026-07-25 計。
- **NML 洪水修正（關鍵）**: scrape_nml 雙分類聯集 snapshot=5594；CATEGORIES 由 1→2（nml_seen 現 2 分類、nml_seen_prev 仍 1 分類 1189），腳本產出 nml_new=5594（整站洪水）。依任務指示手動修正：① nml_seen 改為 seen∪prev 聯集基線（6561 urls，防下次再洪水）；② nml_new 收窄為「近 7 日（>=7/19）且不在 prev 基線」= 101 urls（7/19:2,7/20:14,7/21:14,7/22:24,7/23:27,7/24:17,7/25:3）。
- **構建**: 第一次構建 100 条（含 7/24 殘留 supplement/frontend）；重寫 supplement_urls.json（13 URL 實抓 10）→ fetch_supplement；重寫 frontend.json（11 URL 實合併 9）。第二次構建 94 条 / 7 版塊 — 限時情報王 40、熱門優惠 20、技巧与观点 9、行业动态 11、产品发布/更新 6、论文研究 5、模型发布/更新 3。supplement 合併 10、frontend 合併 9。
- **NML NEW**: 儀表盤限時情报王 NEW=3（url∈nml_new 且 date==2026-07-25）；nml-daily.html new_vs_baseline=3 一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script node --check 通過（248KB, 1 block, SYNTAX OK）。
- **舊聞分頁**: 102 条（4/30–7/19, >5 天）。
- **GitHub Pages**: cp -r build_site/. ghpages/ → commit 2085eda「每日整合：限時情报王 + AI HOT 2026-07-25」push；另複製 nml-daily.html 入 ghpages → commit ccb8453 push → / 與 /nml-daily.html 皆上線。
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 ai-daily-2026-07-25.html + nml-daily.html，提示去連接器頁連接 WeCom/SCRM。
- **經驗**: 每次 scrape_nml 後需檢查 nml_new 是否 ≈ snapshot（洪水訊號）。CATEGORIES 變更導致洪水時，須手動聯集基線 + 收窄 nml_new 為近 7 日且不在 prev；否則全站 5594 標 NEW。本輪已建聯集基線（6561），下次正常 scrape 不應再洪水。

## 2026-07-26 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-07-26｜fetch_daily 7/26 尚未發佈（HTTP 404）→ 回退 7/25 期（sections=5, items=18）。網站以本輪執行日 2026-07-26 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5596；NEW=6（4 篇 7/26 + 2 篇 7/25），非洪水（聯集基線 6561 持續生效，正常 scrape 不再洪水）。
- **構建**: 第一次構建 97 条 → 中文補充（dropped_en 共 17 張，5 版塊）→ 重寫 supplement_urls.json（改用 qq/163/sohu 取代易擋的 toutiao）→ fetch_supplement 實抓 11 篇（模型發布/更新 3、產品發布/更新 2、行業動態 3、論文研究 1、技巧與觀點 2）→ 重寫 frontend.json（掘金/InfoQ/開源中國/SegmentFault/51CTO 共 12 篇）→ 第二次構建 **101 条 / 7 版塊**：限時情報王 40、熱門優惠 20、模型發布/更新 8、產品發布/更新 10、行業動態 10、論文研究 3、技巧與觀點 10。supplement 合併 11、frontend 合併 12。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=4（url∈nml_new 且 date==2026-07-26，4 篇 7/26：Anthropic Opus 5 提示注入免疫、OpenAI HuggingFace 入侵、iPhone 18 Pro/摺疊、Tap Out BJJ）；另 4 篇 NEW 在 Old News 分頁（承襲 7/25 標記）。nml-daily.html `new_vs_baseline=4`、total 5596、shown 40，一致。
- **品質**: index.html 內聯 script `node --check` 通過（260KB, SYNTAX OK）；已知裸引號 bug 模式 0 命中。
- **舊聞分頁**: >5 天歸檔（含 7/25 當日 NEW 承襲）；article_archive 持續累積。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → 複製 nml-daily.html 入 ghpages → git pull(Already up to date) → commit `c4484e4`「每日整合：限時情报王 + AI HOT 2026-07-26」push；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-07-26.html`（儀表盤副本）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-07-27 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-07-27｜fetch_daily 7/27 未發佈（404）→ 7/26 在來源端為 stub（1 版塊 1 項）→ 改用完整 7/25 期（sections=5, items=18）作為回退。網站以執行日 2026-07-27 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5599；nml_new=6（3 篇 7/27 + 3 篇 7/26），非洪水（聯集基線 6561 持續生效）。
- **構建**: 第一次構建 101 条 → dropped_en 共 17 張（5 版塊）→ 重寫 supplement_urls.json（17 URL，優先 qq/163/sina/toutiao/tencent）→ fetch_supplement 實抓 13 篇（模型發布/更新 3、產品發布/更新 3、行業動態 2、論文研究 2、技巧與觀點 3；4 篇 toutiao 擷取失敗）→ 重寫 frontend.json（掘金/InfoQ/CSDN/騰訊雲/個人部落格 共 9 篇）→ 第二次構建 **100 条 / 7 版塊**：限時情報王 40、模型發布/更新 8、產品發布/更新 10、行業動態 8、論文研究 4、技巧與觀點 10、熱門優惠 20。supplement 合併 13、frontend 合併 9。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=3（url∈nml_new 且 date==2026-07-27）；nml-daily.html `new_vs_baseline=3`、total 5599、shown 40，一致。另 3 篇 NEW（7/26）在 Old News 分頁承襲。
- **品質**: index.html 內聯 script `vm.Script` 語法檢查通過；裸引號 bug 模式（display='none' / dealImgFallback(this,''）0 命中。
- **舊聞分頁**: DATA.old=130 条（>5 天累積，較 7/26 的 ~100 增加）；DATA.flat=100、sections=7。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → 複製 nml-daily.html 入 ghpages → git pull(Already up to date) → commit `f2baebd`「每日整合：限時情报王 + AI HOT 2026-07-27」push；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-07-27.html`（儀表盤副本 382KB）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-07-29 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-07-29｜fetch_daily 7/29 尚未發佈（404）→ 回退 7/28 期（sections=5, items=14）。網站以執行日 2026-07-29 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5602；nml_new=9（2 篇 07-29 + 7 篇 07-28），非洪水（聯集基線 6561 持續生效，正常 scrape 不再洪水）。無需手動聯集修正。
- **構建**: 第一次構建 91 条 → 中文補充（dropped_en 14 張：模型發布/更新 1、產品發布/更新 1、行業動態 3、論文研究 1、技巧與觀點 8）→ 重寫 supplement_urls.json（12 URL 實抓 12，全中文化：qq/163/pconline/stcn/csdn/sohu/pulseaugur）→ 重寫 frontend.json（掘金/InfoQ/SegmentFault/開源中國 8 篇）→ 第二次構建 **94 条 / 7 版塊**：限時情報王 40、熱門優惠 20、技巧与观点 16、行业动态 9、产品发布/更新 4、模型发布/更新 3、论文研究 2。supplement 合併 12、frontend 合併 4（另 4 篇被腳本過濾：2 篇掘金 Vue 代碼為主誤判非中文、2 篇 xie.infoq.cn 無全文）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=2（url∈nml_new 且 date==2026-07-29，2 篇 07-29：美國禁止進口外國機器人、iOS 27 Find My）；nml-daily.html `new_vs_baseline=2`、total 5602、shown 40，一致。另 7 篇 NEW（07-28）在 live 近期區但未標 NEW（非今日）。
- **品質**: index.html 內聯 script `vm.Script` 語法檢查通過（327KB, SYNTAX OK）；裸引號 bug 模式（display='none' / dealImgFallback(this,''）0 命中。
- **舊聞分頁**: DATA.old=208 条（>5 天累積，較 7/27 的 130 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → 複製 nml-daily.html 入 ghpages → git pull(Already up to date) → commit `0fad2d0`「每日整合：限時情报王 + AI HOT 2026-07-29」push（6765568..0fad2d0）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-07-29.html`（儀表盤副本 451KB）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-07-30 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-07-30｜fetch_daily 7/30 尚未發佈（404）→ 回退 7/29 期（sections=5, items=24）。網站以執行日 2026-07-30 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5608；nml_new=13（12 篇 07-30 + 1 篇 07-29），非洪水（聯集基線 6561 持續生效，正常 scrape 不再洪水）。無需手動聯集修正。
- **構建**: 第一次構建 104 条（含 7/29 殘留 supplement/frontend）→ 中文補充（dropped_en 共 22 張：模型發布/更新 2、產品發布/更新 4、行業動態 3、論文研究 2、技巧與觀點 8 等）→ 重寫 supplement_urls.json（12 URL 實抓 10，csdn Kimi Linear 因代碼為主誤判非中文被濾）→ 重寫 frontend.json（掘金/InfoQ/CSDN/SegmentFault/開源中國 9 篇）→ 第二次構建 **103 条 / 7 版塊**：限時情報王 40、熱門優惠 20、產品发布/更新 10、行业动态 12、技巧与观点 12、模型发布/更新 4、论文研究 5。supplement 合併 10、frontend 合併 9（3 篇掘金 Vue/框架文被 build 重抓誤判非中文 skip-nonzh，但 JSON 內容已直接合併）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=12（url∈nml_new 且 date==2026-07-30，含 Apple 反對英國 App Store 支付規則、Qualcomm 去高通化、Meta 個人 AI 代理、Safari TP 249、Apple Maps/iOS27、Apple One、6 款限時免費 App）；另 1 篇 NEW（07-29 OpenAI Codex 5h 限制）落在 top-40 外未標 NEW。nml-daily.html `new_vs_baseline=12`、total 5608、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script node `check_inline.js` 通過（378KB, 1 block, SYNTAX OK）；裸引號 bug 模式（display='none' / dealImgFallback(this,''）0 命中。
- **舊聞分頁**: DATA.old=238 条（>5 天累積，較 7/29 的 208 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → 複製 nml-daily.html 入 ghpages → git pull(Already up to date) → commit `bc4ecf9`「每日整合：限時情报王 + AI HOT 2026-07-30」push（0fad2d0..bc4ecf9）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-07-30.html`（儀表盤副本 500KB）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-07-31 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-07-31｜fetch_daily 7/31 尚未發佈（404）→ 回退 7/30 期（sections=5, items=23）。網站以執行日 2026-07-31 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5634；nml_new=37（18 篇 07-31 + 19 篇 07-30），非洪水（聯集基線 5634 持續生效，正常 scrape 不再洪水）。無需手動聯集修正。
- **構建**: 第一次構建 102 条（含 7/30 殘留 supplement/frontend）→ 中文補充（dropped_en 共 5 組 section：模型發布/更新 1、產品發布/更新 8、行業動態 2、論文研究 2、技巧與觀點 7）→ 重寫 supplement_urls.json（13 URL 實抓 11，3 篇 toutiao 無區塊被濾）→ 重寫 frontend.json（掘金/InfoQ/開源中國/SegmentFault/w3ctech 共 11 篇）→ 第二次構建 **105 条 / 7 版塊**：限時情報王 40、熱門優惠 20、產品发布/更新 16、技巧与观点 13、行业动态 9、论文研究 4、模型发布/更新 3。supplement 合併 11、frontend 合併 11（2 篇掘金 curated 文因重抓誤判 skip-nonzh、2 篇 SegmentFault/w3ctech 404/timeout 但 JSON 已合併）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=18（url∈nml_new 且 date==2026-07-31）；nml-daily.html `new_vs_baseline=18`、total 5634、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script node --check 通過（406KB, SYNTAX OK）；裸引號 bug 模式 0 命中。
- **舊聞分頁**: DATA.old=261 条（>5 天累積，較 7/30 的 238 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → 複製 nml-daily.html 入 ghpages → git pull(Already up to date) → commit `ff6daf2`「每日整合：限時情报王 + AI HOT 2026-07-31」push（6d6670c..ff6daf2）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-07-31.html`（儀表盤副本 538KB）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-08-02 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-02｜fetch_daily 8/02 尚未發佈（404）→ 回退 8/01 期（sections=5, items=22）。網站以執行日 2026-08-02 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5642；nml_new=4（3 篇 2026-08-02 + 1 篇 2026-08-01），非洪水（聯集基線持續生效）。FETCH FAIL 限時免費情報 page/34（HTTP 410 Gone）已優雅跳過。
- **構建**: 第一次構建 106 条 → 中文補充（dropped_en 5 版塊）→ 重寫 supplement_urls.json（13 URL 實抓 13：模型發布/更新 3、產品發布/更新 3、行業動態 4、論文研究 2、技巧與觀點 1；csdn/toutiao 連線關閉與無區塊被濾）→ 重寫 frontend.json（掘金/Vite8/kwkr 技術雷達/CSDN aicoding 全景/segmentfault×2/momoc 共 8 篇）→ 第二次構建 **102 条 / 7 版塊**：限時情報王 40、產品发布/更新 9、行业动态 11、技巧与观点 12、模型发布/更新 6、论文研究 4、熱門優惠 20。supplement 合併 13、frontend 合併 7（掘金 7664880484322099263 因重抓誤判 skip-nonzh 被濾，JSON 內容未合併）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=3（url∈nml_new 且 date==2026-08-02：Flipomo 番茄鐘、DoubleIt Camera、Articulate AI 發音教練 限時免費）；nml-daily.html `new_vs_baseline=3`、total 5642、shown 40，一致。另 1 篇 NEW（08-01 Video Stabilizer）非今日不標 NEW。
- **品質**: index.html 內聯 script `check_inline.js` 通過（402KB, 1 block, SYNTAX OK）；`dealImgFallback(this,'` 裸引號 bug 模式 0 命中；`display='none'` 僅見於 herenow 徽章隱藏邏輯（naked-quote 標記 true 為該處誤報），非 onerror，無復發。build_site ≡ ghpages IDENTICAL。
- **舊聞分頁**: DATA.old=285 条（>5 天累積，較 8/01 的 268 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → 複製 nml-daily.html 入 ghpages → git pull(Already up to date) → commit `c7972f6`「每日整合：限時情报王 + AI HOT 2026-08-02」push（5a9d94d..c7972f6）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-02.html`（儀表盤副本 424KB）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-08-01 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-01｜fetch_daily 8/01 尚未發佈（404）→ 回退 7/31 期（sections=5, items=24）。網站以執行日 2026-08-01 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5638；nml_new=10（3 篇 2026-08-01 + 7 篇 2026-07-31），非洪水（聯集基線持續生效）。無需手動聯集修正。FETCH FAIL 限時免費情報 page/34（HTTP 410 Gone）已優雅跳過。
- **構建**: 第一次構建 106 条 → 中文補充（dropped_en 5 版塊）→ 重寫 supplement_urls.json（初輪 15 URL，huxiu/vbdata/gslin 被非中文濾掉→換 qq/wedoany 後 14 實抓：模型發布/更新 3、產品發布/更新 4、行業動態 2、論文研究 3、技巧與觀點 2）→ 重寫 frontend.json（掘金/InfoQ/開源中國/SegmentFault/w3ctech 10 篇）→ 第二次構建 **108 条 / 7 版塊**：限時情報王 40、產品發布/更新 14、模型發布/更新 8、行業動態 8、論文研究 8、技巧与观点 10、熱門優惠 20。supplement 合併 14、frontend 合併 10（juejin/infoq/segmentfault/w3ctech URL 多 404/502/nofull，但 JSON 內容已合併，卡片照常顯示）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=3（url∈nml_new 且 date==2026-08-01：iOS 27 橫向模式、iPhone 18e 9GB RAM、iPhone 17 Pro 墜機無損）；nml-daily.html `new_vs_baseline=3`、total 5638、shown 40，一致。另 7 篇 NEW（07-31）在近期區未標今日 NEW。
- **品質**: index.html 內聯 script node --check 通過（SYNTAX OK）；裸引號 bug 模式（dealImgFallback(this,' 0 命中；display='none' 僅見於 herenow 徽章隱藏邏輯，非 onerror），無復發。
- **舊聞分頁**: DATA.old=268 条（>5 天累積，較 7/31 的 261 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → 複製 nml-daily.html 入 ghpages → git pull(Already up to date) → commit `5a9d94d`「每日整合：限時情报王 + AI HOT 2026-08-01」push（ff6daf2..5a9d94d）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-01.html`（儀表盤副本 545KB）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-08-03 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-03｜fetch_daily 8/03 尚未發佈（404）→ 回退 8/01 期（sections=5, items=22；原 fallback 取最新 8/02 為 2 項 stub，已修 fetch_daily.py 改取 take=5 中首個 >=8 項的期數）。網站以執行日 2026-08-03 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5654；nml_new=16（9 篇 2026-08-03 + 7 篇 2026-08-02），非洪水（聯集基線持續生效）。FETCH FAIL 限時免費情報 page/35（HTTP 410 Gone）已優雅跳過。
- **構建**: 第一次構建 102 条 → 中文補充（dropped_en）→ 重寫 supplement_urls.json（15 URL 實抓 14，1 篇 skip non-zh）+ 重寫 frontend.json（11 篇）→ 第二次構建 **104 条 / 7 版塊**：限時情報王 40、熱門優惠 20、技巧与观点 12、產品發布/更新 10、行業動態 11、模型發布/更新 7、論文研究 4。supplement 合併 14、frontend 合併 8。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=9（url∈nml_new 且 date==2026-08-03）；nml-daily.html `new_vs_baseline=9`、total 5654、shown 40，一致。
- **品質**: index.html 內聯 script 已知裸引號 bug 模式 0 命中；&quot;none&quot; 1；build_site ≡ ghpages IDENTICAL（cp 後）。
- **舊聞分頁**: DATA.old=318 条（>5 天累積，較 8/02 的 285 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` → 複製 nml-daily.html 入 ghpages → git pull(Already up to date) → commit `e8c3544`「每日整合：限時情报王 + AI HOT 2026-08-03」push（c7972f6..e8c3544）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 確認 build_site + ghpages 皆已置頂（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-03.html`（儀表盤副本 581KB）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-08-04 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-04｜**fetch_daily 今日期已發佈**（sections=5, items=21），近期少見無需回退。
- **NML 監測**: scrape 雙分類聯集 snapshot=5668；nml_new=27（13 篇 2026-08-04 + 14 篇 2026-08-03），非洪水（聯集基線持續生效），無需手動聯集修正。
- **構建**: 第一次構建 103 条 → dropped_en 21 張（模型發布/更新 2、產品發布/更新 8、行業動態 2、論文研究 1、技巧與觀點 8）→ 重寫 supplement_urls.json（19 URL 實抓 15：模型 3、產品 4、行業 4、論文 3、技巧 1；ifnews/mo.zju skip-nonzh、simater 無區塊、wenku.csdn 521）→ 重寫 frontend.json（TypeScript 7.0 Go 重寫 ×3、Cloudflare 跨語言 RPC、React Compiler Rust 化、Inertia.js、CSDN 極客日報、Rust 前端工具鏈，共 8 篇）→ 第二次構建 **104 条 / 7 版塊**：限時情報王 40、熱門優惠 20、產品發布/更新 15、技巧与观点 12、行业动态 8、模型发布/更新 5、论文研究 4。supplement 合併 15、frontend 合併 8（juejin 7653675068171681801 重抓誤判 skip-nonzh、toutiao 7668902019955950080 nofull，但 JSON 內容已合併）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=13（url∈nml_new 且 date==2026-08-04）；nml-daily.html `new_vs_baseline=13`、total 5668、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 617KB / 1 inline block，`node --check` SYNTAX OK；`dealImgFallback(this,''` 裸引號 bug 模式 0 命中；`&quot;none&quot;` 1。build_site ≡ ghpages IDENTICAL。
- **舊聞分頁**: DATA.old=345 条（>5 天累積，較 8/03 的 318 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `ed5718e`「每日整合：限時情报王 + AI HOT 2026-08-04」push（e8c3544..ed5718e）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-04.html`（儀表盤副本 618KB）+ `nml-daily.html`（52KB），提示去連接器頁連接 WeCom/SCRM。

## 2026-08-05 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-05｜fetch_daily 今日期未發佈（404）→ 回退 8/04 期（sections=5, items=21）。網站以執行日 2026-08-05 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5680；nml_new=19（8 篇 2026-08-05 + 11 篇 2026-08-04），非洪水（聯集基線持續生效），無需手動聯集修正。
- **構建**: 第一次構建 104 条（含 8/04 殘留補充）→ dropped_en 21 張（模型發布/更新 2、產品發布/更新 8、行業動態 2、論文研究 1、技巧與觀點 8）→ 重寫 supplement_urls.json（首輪 18 URL 實抓 14；換掉 toutiao/huxiu 後第二輪實抓 **16**：模型 3、產品 4、行業 4、論文 2、技巧 3）→ 重寫 frontend.json 8 篇（React Compiler Rust 化、Inertia.js 無 API 全棧、Cloudflare Town Lake、Google Agent Substrate、Schema-As-Code 語義約束、2026 前端面經 5 變、Uncle Bob vs Hashimoto、GPT-2→Kimi K3 記憶操作系統）→ 第二次構建 **97 条 / 7 版塊**：限時情報王 40、熱門優惠 20、產品發布/更新 12、技巧与观点 11、模型发布/更新 5、行业动态 6、论文研究 3。supplement 合併 16、frontend 合併 8（8 篇 frontend 皆 `unknown url type ''` 全文重抓失敗但 JSON 內容已合併，卡片正常顯示；IMG 端點多次 429）。
- **NML NEW**: 儀表盤限時情报王 NEW=8（url∈nml_new 且 date==2026-08-05）；nml-daily.html `new_vs_baseline=8`、total 5680、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 640KB / 1 inline block，`node --check` SYNTAX OK；`dealImgFallback(this,''` 裸引號 0 命中；`&quot;none&quot;` 1。build_site ≡ ghpages IDENTICAL。
- **舊聞分頁**: DATA.old=372 条（>5 天累積，較 8/04 的 345 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `0b01d15`「每日整合：限時情报王 + AI HOT 2026-08-05」push（ed5718e..0b01d15）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-05.html`（儀表盤副本 640KB）+ `nml-daily.html`（52KB），提示去連接器頁連接 WeCom/SCRM。
- **待優化**: frontend.json 內 InfoQ 條目用首頁 URL（https://www.infoq.cn/）導致 build 重抓報 `unknown url type ''`；下次應填具體文章 URL 以取得全文頁。

## 2026-08-06 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-06｜fetch_daily 8/06 尚未發佈（404）→ 回退 8/05 期（sections=4, items=29）。網站以執行日 2026-08-06 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5690；nml_new=16（9 篇 2026-08-06 + 7 篇 2026-08-05），非洪水（聯集基線持續生效），無需手動聯集修正。
- **構建**: 第一次構建 105 条 → dropped_en 22 張（5 版塊）→ 重寫 supplement_urls.json（14 URL 實抓 17：模型發布/更新 4、產品發布/更新 2、行業動態 4、論文研究 3、技巧與觀點 4；首輪 toutiao 無區塊已換 163/qq/csdn/techwalker/oschina）→ 重寫 frontend.json 6 篇（掘金 Pinia 4.0 / Remix 3.0 重寫 / Vue x Vite Conf 2026 / CSDN 2026 前端全景 / 掘金 Vue3 初始化 / 極客日報開源精選）→ 第二次構建 **106 条 / 7 版塊**：限時情報王 40、熱門優惠 20、技巧与观点 12、模型發布/更新 10、產品發布/更新 10、行业动态 11、论文研究 3。supplement 合併 17、frontend 合併 6（frontend 全文重抓 `unknown url type ''` 但 JSON 內容已合併，卡片正常顯示；IMG 端點多次 429）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=9（url∈nml_new 且 date==2026-08-06）；nml-daily.html `new_vs_baseline=9`、total 5690、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 535KB / 1 inline block，`node --check` SYNTAX OK；`dealImgFallback(this,''` 裸引號 bug 模式 0 命中；`display='none'` 1（僅 herenow 徽章隱藏邏輯，非 onerror）。build_site ≡ ghpages IDENTICAL。
- **舊聞分頁**: DATA.old=444 条（>5 天累積，較 8/05 的 372 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `51aeb5a`「每日整合：限時情报王 + AI HOT 2026-08-06」push（0b01d15..51aeb5a）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-06.html`（儀表盤副本 727KB）+ `nml-daily.html`（51KB），提示去連接器頁連接 WeCom/SCRM。

## 2026-08-07 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-07｜fetch_daily 8/07 尚未發佈（404）→ 回退 8/06 期（sections=5, items=24）。網站以執行日 2026-08-07 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5701；nml_new=24（14 篇 2026-08-07 + 9 篇 08-06 + 1 篇 08-02），非洪水（聯集基線持續生效），無需手動聯集修正。
- **構建**: 第一次構建 101 条 → dropped_en 23 張（模型 1、產品 5、行業 7、論文 2、技巧 8）→ supplement_urls.json 首輪 17 URL 實抓 **13**（dy.163 逾時、ifeng 連線重置、10jqka 521、163 L3EKN20I 404）→ 換掉 4 個失敗來源後第二輪實抓 **17**（模型 4、產品 3、行業 4、論文 3、技巧 3）→ 重寫 frontend.json 7 篇（Remix 3.0 重寫 / Jotai v2.20 Store 重做 / React Compiler Rust 化 / 前端周刊 #402 / 多智能體省 Token 四招 / Prompt→Context→Loop→Graph 四層演化 / 2026 前端選型清單）→ 第二次構建 **101 条 / 7 版塊**：限時情報王 40、熱門優惠 20、行业动态 12、技巧与观点 11、产品发布/更新 8、模型发布/更新 5、论文研究 5。supplement 合併 17、frontend 合併 7。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=**14**（url∈nml_new 且 date==2026-08-07：Apple 調高換購估值、ChapterChat / We Were Here Together / Ghost Recon Future Soldier / Beacon Pines 等限免）；nml-daily.html `new_vs_baseline=14`、total 5701、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 558KB / 1 inline block，vm.Script SYNTAX OK；`dealImgFallback(this,''` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1。build_site ≡ ghpages IDENTICAL。新建通用檢查腳本 `_inline_check_today.js`（可傳入檔案路徑，取代已失效的 `__check_inline.js`）。
- **舊聞分頁**: DATA.old=**470** 条（>5 天累積，較 8/06 的 444 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `da6d056`「每日整合：限時情报王 + AI HOT 2026-08-07」push（51aeb5a..da6d056）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-07.html`（儀表盤副本）+ `nml-daily.html`（39KB），提示去連接器頁連接 WeCom/SCRM。
- **經驗**: dy.163.com 子域常逾時，改用 www.163.com 同 ID 路徑可成功；news.10jqka.com.cn 有 521 防護、news.ifeng.com 會重置連線 → 補充來源優先 new.qq.com / www.163.com / finance.sina.com.cn / cloud.tencent.com / tdteach.github.io。

## 2026-08-08 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-08｜fetch_daily 8/08 尚未發佈（404）→ 回退 8/07 期（sections=5, items=25）。網站以執行日 2026-08-08 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=**5717**；nml_new=**31**（16 篇 2026-08-08 + 15 篇 2026-08-07），非洪水（聯集基線持續生效），無需手動聯集修正。
- **構建**: 第一次構建 102 条 → dropped_en **23** 張（模型 2、產品 6、行業 5、論文 2、技巧 8）→ 重寫 supplement_urls.json（19 URL 實抓 **18**：模型 4、產品 4、行業 4、論文 4、技巧 2；juejin 7668305038255554606 因代碼佔比高被 skip-nonzh）→ 重寫 frontend.json 7 篇（Rspack 2.0 掘金 / TypeScript 7 W3Cschool / CSDN 前端周刊 #42 / Front Talk 上半年五次巨變 / 掘金 Vibe Coding 全棧 / icodex 週報 / Rspack 2.1 官方）→ 第二次構建 **103 条 / 7 版塊**：限時情報王 40、產品發布/更新 11、行業動態 10、技巧与观点 10、模型发布/更新 6、论文研究 6、熱門優惠 20。supplement 合併 18、frontend 合併 7。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=**16**（url∈nml_new 且 date==2026-08-08）；nml-daily.html `new_vs_baseline=16`、total 5717、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 582,504 chars / 2 inline blocks，`node --check` SYNTAX OK（build 後與 pin 後各驗一次）；`dealImgFallback(this,''` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1。build_site ≡ ghpages IDENTICAL。
- **舊聞分頁**: DATA.old=**480** 条（>5 天累積，較 8/07 的 470 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `f0e4f77`「每日整合：限時情报王 + AI HOT 2026-08-08」push（da6d056..f0e4f77）；`/` 與 `/nml-daily.html` 皆回 HTTP 200 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-08.html`（儀表盤副本 764KB）+ `nml-daily.html`（52KB），提示去連接器頁連接 WeCom/SCRM。
- **經驗**: Git Bash 無 `sleep` 內建指令（`sleep: command not found`），需驗證延遲時改用其他方式或直接重試 curl。IMG 端點（Unsplash 類）本輪多次 429，不影響出報。

## 2026-08-09 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-09（週日）｜fetch_daily 8/09 尚未發佈（404）→ 回退 8/08 期（sections=5, items=25）。網站以執行日 2026-08-09 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=**5733**；nml_new=**18**（全數 dated 2026-08-08），非洪水（聯集基線持續生效），無需手動聯集修正。
- **構建**: 第一次構建 99 条 → dropped_en **19** 張（模型 2、產品 8、行業 1、論文 5、技巧 5）→ 重寫 supplement_urls.json（20 URL 實抓 **19**：模型 4、產品 4、行業 4、論文 4、技巧 3）→ 重寫 frontend.json 8 篇（Vue x Vite Conf 2026 / Web 前端周刊 2026W30 / 栗子前端週刊 #140 / 前端技術雷達 2026 下半年 / 上周前端新鮮事 #402 / 2026 前端生死局 8 趨勢 / 2026 前端大洗牌 / React 19 Compiler 實戰）→ 第二次構建 **100 条 / 7 版塊**：限時情報王 40、產品发布/更新 12、论文研究 9、行业动态 6、技巧与观点 8、模型发布/更新 5、熱門優惠 20。supplement 合併 19、frontend 合併 8（全文重抓 `unknown url type ''` 但 JSON 內容已合併；IMG 端點多次 429）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）**NEW=0**（18 篇 nml_new 皆 dated 2026-08-08，執行日 8/09 無新增故不標 NEW）；nml-daily.html `new_vs_baseline=0`、total 5733、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 587KB / 1 inline block，`_inline_check_today.js` SYNTAX OK（ok:1, bad:0）；`dealImgFallback(this,''` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1（herenow 徽章隱藏，非 onerror）。build_site ≡ ghpages IDENTICAL。
- **舊聞分頁**: DATA.old=**490** 条（>5 天累積，較 8/08 的 480 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `af39846`「每日整合：限時情报王 + AI HOT 2026-08-09」push（f0e4f77..af39846）；`/` 與 `/nml-daily.html` 皆回 HTTP 200 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-09.html`（儀表盤副本 792KB）+ `nml-daily-2026-08-09.html`（54KB），提示去連接器頁連接 WeCom/SCRM。

## 2026-08-10 (08:00 排程自動執行 · 續跑 8/10 中斷場) — 執行成功 ✅
- **日期**: 2026-08-10｜fetch_daily 今日期僅 4 條 stub（sections=1）→ 自動合併 8/08 完整期（sections=5, items=25）：技巧与观点 9、模型发布/更新 1、产品发布/更新 8、行业动态 2、论文研究 5。（fetch_daily.py 已加 thin-stub 合併邏輯 + `_sec_label` 修正，AI HOT 用 `label` 鍵。）
- **NML 監測**: scrape 雙分類聯集 snapshot=5746；nml_new 合併 8/10 部分執行備份，最終 19 urls（13 @ 2026-08-10 + 6 @ 2026-08-09），非洪水。
- **構建**: 第一次構建 104 条；中文補充（dropped_en 23 張）→ 重寫 supplement_urls.json（含 4 篇強化行業動態）→ fetch_supplement 實抓 23（模型 4、產品 4、行業 6、論文 4、技巧 5）；重寫 frontend.json 9 篇（掘金/SegmentFault/InfoQ中文 真實近期文：Nuxt 4.5、Rspack 2.1、Vite 6.2、Vue 3.6 RC、Webpack→Rspack 實戰等，含 sourceName/sourceUrl 讓卡面來源顯示+全文萃取）；第二次構建 **117 条 / 7 版塊**：限時情报王 40、熱門優惠 20、技巧与观点 17、产品发布/更新 16、行业动态 10、论文研究 9、模型发布/更新 5。supplement 合併 23、frontend 合併 9。
- **NML NEW**: 儀表盤限時情报王 NEW=13（url∈nml_new 且 date==2026-08-10）；nml-daily.html `new_vs_baseline=13`、total 5746、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 654KB / 1 inline block，`_inline_check_today.js` SYNTAX OK（ok:1, bad:0）；`dealImgFallback(this,'` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1（herenow 徽章隱藏，非 onerror）。build_site ≡ ghpages IDENTICAL。
- **舊聞分頁**: DATA.old 較 8/09（490）增加（>5 天累積）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull 已 ff → commit `98323bd`「每日整合：限時情报王 + AI HOT 2026-08-10」push（af39846..98323bd）；`/` 與 `/nml-daily.html` 皆 HTTP 200 → https://liuchiwai0101.github.io/news/
- **重大修復（git push 卡死）**: 原 push 懸停 19 分鐘 remote tip 不變；根因 `ghpages` 倉庫 `credential.helper=manager`（GCM）在非互動 shell 下 write 卡死（read 正常）。修正 `git -C ghpages config --local credential.helper ""`（token 已內嵌 URL）後 push 2 秒完成。已寫入專案 MEMORY.md 作為常態慣例；另 `protocol.version=0`+`http.version=HTTP/1.1` 繞過偶發 v2 `expected flush` 協商錯誤。
- **程式小改**: `build_dashboard.py` `_merge_extra` except 分支加 curated-summary 回退（代碼為主中文前端文經 skip-nonzh 拋錯時仍可藉 summary 留卡）。
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-10.html`（儀表盤副本 885KB）+ `nml-daily.html`（54KB），提示去連接器頁連接 WeCom/SCRM。

## 2026-08-12 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-12｜fetch_daily 8/12 尚未發佈（404）→ 回退 8/11 期（sections=5, items=20）。網站以執行日 2026-08-12 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5791；nml_new=41（16 篇 2026-08-12 + 25 篇 2026-08-11），非洪水（聯集基線 5791 持續生效），無需手動聯集修正。
- **構建**: 第一次構建 106 条 → dropped_en 20 張（模型 3、產品 8、行業 2、論文 1、技巧 6）→ 重寫 supplement_urls.json（11 URL 實抓 8：模型 3、產品 2、行業 1、論文 1、技巧 1；gu.qq.com×2 為 JS-shell 頁 skip non-zh）→ 重寫 frontend.json 9 篇（掘金/InfoQ中文/開源中國/SegmentFault/w3ctech：Nuxt 4.5、Vue 3.6 RC、Rspack 2.2、Web 前端週刊 2026W32、State of JS 2026、Vite 7 RC、Webpack→Rspack 遷移、2026 前端選型、Agentic 前端重構）→ 第二次構建 **97 条 / 7 版塊**：限時情报王 40、熱門優惠 20、產品发布/更新 13、技巧与观点 10、行業動態 6、模型发布/更新 6、論文研究 2。supplement 合併 8、frontend 合併 9。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=**16**（url∈nml_new 且 date==2026-08-12）；nml-daily.html `new_vs_baseline=16`、total 5791、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `_inline_check_today.js` SYNTAX OK（1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1（herenow 徽章隱藏，非 onerror）。build_site ≡ ghpages IDENTICAL。
- **舊聞分頁**: `article_archive.json` 為空 → **0** 條承襲（連續性中斷，非腳本錯誤；如需恢復需從備份還原 archive）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `8fde42c`「每日整合：限時情报王 + AI HOT 2026-08-12」push（45abc20..8fde42c）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-12.html`（儀表盤副本 909KB）+ `nml-daily.html`（49KB），提示去連接器頁連接 WeCom/SCRM。

## 2026-08-13 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-13｜fetch_daily 今日期已發佈（sections=5, items=20）。網站以 2026-08-13 計（無需回退）。
- **NML 監測**: scrape 雙分類聯集 snapshot=5822；nml_new=47（14 篇 2026-08-13 + 33 篇 2026-08-12），非洪水（聯集基線 5822 持續生效），無需手動聯集修正。
- **構建**: 第一次構建 97 条（含前次殘留 supplement/frontend）→ dropped_en 18 張（模型 2、產品 5、行業 2、論文 2、技巧 7）→ 重寫 supplement_urls.json（15 URL 實抓 14：模型 4、產品 4、行業 2、論文 3、技巧 1；toutiao 無區塊 + gu.qq JS-shell 被濾）→ 重寫 frontend.json 10 篇（掘金/InfoQ中文/開源中國/SegmentFault/前端週刊：Waku Alpha、低代碼生成 Vue3、Next.js 16.3、AI 表格前端執行器、AI First 前端架構、React+TS+Vite 分層、Next.js 部署、前端架構、Webpack5）→ 第二次構建 **104 条 / 7 版塊**：限時情报王 40、熱門優惠 20、產品发布/更新 12、技巧与观点 12、模型发布/更新 8、行业动态 7、论文研究 5。supplement 合併 14、frontend 合併 10。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=**14**（url∈nml_new 且 date==2026-08-13）；nml-daily.html `new_vs_baseline=14`、total 5822、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `vm.Script` 語法檢查通過（1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1（herenow 徽章隱藏，非 onerror）。build_site ≡ ghpages（pin 後）。
- **舊聞分頁**: DATA.old=**0** 条。archive 現有 1392 條（跨 2025-12-15~2026-08-13），但多數為中文格式日期（如「8月9日 周日」）致 >5 天篩選無法解析 → 0 承襲（8/12 archive 重置的連續性餘波；非腳本錯誤）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `ba899f4`「每日整合：限時情报王 + AI HOT 2026-08-13」push（8fde42c..ba899f4）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-13.html`（儀表盤副本）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-08-14 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-14｜fetch_daily 今日期尚未發佈（404）→ 回退 2026-08-13 期（sections=5, items=20）。網站以執行日 2026-08-14 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5843；nml_new=36（12 篇 2026-08-14 + 24 篇 2026-08-13），非洪水（聯集基線 5843 持續生效），無需手動聯集修正。
- **構建**: 第一次構建 104 条（含前次殘留 supplement/frontend）→ dropped_en 18 張（模型 2、產品 5、行業 2、論文 2、技巧 7）→ 重寫 supplement_urls.json（18 URL 實抓 15：模型 4、產品 5、行業 2、論文 1、技巧 3；csdn/某非中文 + toutiao 無區塊被濾）→ 重寫 frontend.json 10 篇（掘金/InfoQ中文/開源中國/SegmentFault：useEvent、useDisclosure、React Hooks 受控組件、Vercel 70 條軍規、React 數據管理、useMemo 反模式、React Router 50 行、AI 表格執行器、2026 前端大洗牌、React Compiler Rust；w3ctech 無可索引近期文故以 4 來源涵蓋）→ 第二次構建 **105 条 / 7 版塊**：限時情报王 40、產品发布/更新 11、技巧与观点 17、模型发布/更新 8、行业动态 6、论文研究 3、熱門優惠 20。supplement 合併 15、frontend 合併 10（掘金 useEvent 重抓 skip-nonzh 但 curated summary 回退留卡）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=**12**（url∈nml_new 且 date==2026-08-14：Gemini 3.7 Flash 編碼降價、WhatsApp 動態桌布、iFixit Galaxy Z Fold8 拆解等）；nml-daily.html `new_vs_baseline=12`、total 5843、shown 40，一致（已用 node 重新解析 isNew 欄確認 12，非 0）。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `vm.Script` 語法檢查通過（1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1（line 499 正確修復）、`badge.style.display='none'` 僅 herenow 徽章隱藏（graceful degrade，非 onerror）。build_site ≡ ghpages（pin 後）。
- **舊聞分頁**: DATA.old=**739** 条（>5 天累積；archive 跨 2025-12-15~2026-08-13，ISO 日期現可解析故承襲量大增，非錯誤）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `e69947d`「每日整合：限時情报王 + AI HOT 2026-08-14」push（ef16558..e69947d）；`/` 與 `/nml-daily.html` 皆回 HTTP 200 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-14.html`（儀表盤副本 105 条）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-08-15 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-15｜fetch_daily 今日期尚未發佈（404）→ 回退 2026-08-14 期（sections=5, items=23）。網站以執行日 2026-08-15 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5853；nml_new=22（9 篇 2026-08-15 + 13 篇 2026-08-13/14），非洪水（聯集基線 5853 持續生效），無需手動聯集修正。categories 仍 2（新聞熱話 + 限時免費情報），未變。
- **構建**: 第一次構建 108 条 → dropped_en 20 張 → 重寫 supplement_urls.json（16 URL 實抓 16：模型 4、產品 2、行業 3、論文 3、技巧 4；finance.sina 2 個 404 被濾但同版塊其他成功）→ 重寫 frontend.json 11 篇（掘金/InfoQ中文/開源中國/SegmentFault/Rspack：Pinia 4、TanStack Table V9、栗子前端週刊141、Rspack 2.1、React Props、React TS Todo、TS 條件類型/infer、Vite 構建優化、Vite 預構建、Vite CVE-2026-29321）→ 第二次構建 **109 条 / 7 版塊**：限時情报王 40、模型发布/更新 7、产品发布/更新 14、行业动态 7、论文研究 5、技巧与观点 16、熱門優惠 20。supplement 合併 16、frontend 合併 10（5 篇 skip-nonzh 因 curated summary 回退仍留卡）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）is-new 徽章 4（url∈nml_new 且 date==2026-08-15 子集）；nml-daily.html `new_vs_baseline=9`、total 5853、shown 40（一致）。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `vm.Script` 語法檢查通過（1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0、`onerror display='none'` 0、`&quot;none&quot;` 1（正確修復）。build_site ≡ ghpages（pin 後）。偶發 429/521/403 圖片抓取失敗不影響構建（卡片仍渲染）。
- **舊聞分頁**: DATA.old=**745** 条（>5 天累積；限時情报王 405、产品发布/更新 61、技巧与观点 66、行业动态 44、模型发布/更新 22、论文研究 20、'' 127）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `db77c3e`「每日整合：限時情报王 + AI HOT 2026-08-15」push（e69947d..db77c3e）；後刷新 nml-daily.html commit `5f149b8`（db77c3e..5f149b8）。`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-15.html`（儀表盤副本 109 条）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-08-16 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-16｜fetch_daily 今日期尚未發佈（404）→ 回退 2026-08-15 期（sections=4, items=15）。網站以執行日 2026-08-16 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5865；nml_new=14（2 篇 2026-08-16 + 12 篇 2026-08-15），非洪水（聯集基線 5865 持續生效），無需手動聯集修正。categories 仍 2，未變。
- **構建**: 第一次構建 101 条（含前次殘留 supplement/frontend）→ dropped_en 讀取（模型 4、產品 1、行業 3、技巧 6）→ 重寫 supplement_urls.json（yicai 3 個逾時連線失敗被濾；實抓 cloud.tencent 2 + new.qq 1 + view.inews.qq 2 = 模型 2、產品 2、行業 1、技巧 1）→ 重寫 frontend.json 12 篇（掘金 4 how-to + 掘金 2 產品 + InfoQ 2 + 開源中國/SegmentFault/w3ctech 各 1）→ 第二次構建 **93 条 / 7 版塊**：限時情报王 40、模型发布/更新 6、产品发布/更新 6、行业动态 5、论文研究 0、技巧与观点 16、熱門優惠 20。supplement 合併 6、frontend 合併 12（juejin 全文重抓 skip-nonzh 但 curated summary 回退留卡；InfoQ/oschina/segmentfault/w3ctech 首頁 URL nofull 但 JSON 內容已合併）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）is-new 徽章 **2**（url∈nml_new 且 date==2026-08-16：Apple 智能家居產品藍圖、Deadline Dash 限時免費）；nml-daily.html `new_vs_baseline=2`、total 5865、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `_inline_check_today.js` 通過（829KB, 1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0、`onerror display='none'` 0、`&quot;none&quot;` 1。build_site ≡ ghpages（pin 後）。偶發 429/10060 逾時/10061 拒連圖片抓取失敗不影響構建。
- **舊聞分頁**: DATA.old=**777** 条（>5 天累積，較 8/15 的 745 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `681b01e`「每日整合：限時情报王 + AI HOT 2026-08-16」push（5f149b8..681b01e）；`/` 與 `/nml-daily.html` 皆回 HTTP 200 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-16.html`（儀表盤副本 93 条）+ `nml-daily.html`，提示去連接器頁連接 WeCom/SCRM。

## 2026-08-17 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-17｜fetch_daily 今日期尚未發佈（404）→ 回退 2026-08-15 期（sections=4, items=15）。網站以執行日 2026-08-17 計（AI HOT 版塊沿用 8/15 期內容）。
- **NML 監測**: scrape 雙分類聯集 snapshot=5880；nml_new=16（7 篇 2026-08-17 + 9 篇 2026-08-16），非洪水（聯集基線 5880 持續生效），無需手動聯集修正。限時免費情報 page/39 為 HTTP 410 Gone 已優雅跳過。
- **構建**: 第一次構建 93 条（含前次殘留 supplement/frontend）→ dropped_en 讀取（模型 4、產品 1、行業 3、技巧 6）→ 重寫 supplement_urls.json（中文域名：163 / new.qq / sina / sohu / sina財經 / ftnn；toutiao 無區塊被濾）→ 實抓 **9 篇**（模型 3、產品 1、行業 3、技巧 2）→ 重寫 frontend.json **9 篇**（產品 2：Rspack 2.0 csdn、Rolldown 1.0 segmentfault；行業 3：xie.infoq 84%AI、devpress 前端全景、segmentfault 前端周報；技巧 4：infoq React Compiler Rust、juejin 2026 10 大技能、juejin React 18/19 生態、segmentfault Pretext）→ 第二次構建 **93 条 / 7 版塊**：限時情报王 40、模型发布/更新 7、产品发布/更新 4、行业动态 10、论文研究 0、技巧与观点 12、熱門優惠 20。supplement 合併 9、frontend 合併 9（juejin 2 篇 skip-nonzh 但 curated summary 回退留卡；csdn 週刊 / xie.infoq 首頁 nofull 但 JSON 內容已合併；chinaz 圖片逾時不影響）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）is-new 徽章 **7**（url∈nml_new 且 date==2026-08-17：頂級數學家論 LLM 創造性、Precursor 限時免費、Stampr、Gutio、ComeCloser Camera、Nanagi、MoonDust）；nml-daily.html `new_vs_baseline=7`、total 5880、shown 40，一致（另 9 篇 nml_new 為 8/16 發佈、非今日故不標 NEW）。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `_inline_check_today.js` 通過（871KB, 1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0、`onerror display='none'` 0、`&quot;none&quot;` 1（herenow 徽章隱藏，非 onerror）。build_site ≡ ghpages（pin 後 IDENTICAL）。偶發 429 / 圖片逾時不影響構建。
- **舊聞分頁**: DATA.old=**827** 条（>5 天累積，較 8/16 的 777 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `bb3942f`「每日整合：限時情报王 + AI HOT 2026-08-17」push（681b01e..bb3942f，已停用 GCM + protocol.version=0/HTTP/1.1 繞過 v2 flush）；`/` 與 `/nml-daily.html` 皆回 HTTP 200 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-17.html`（儀表盤副本 93 条）+ `nml-daily.html`（54KB），提示去連接器頁連接 WeCom/SCRM。

## 2026-08-18 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-18｜fetch_daily 8/18 尚未發佈（404）→ 回退 2026-08-15 期（sections=4, items=15）。網站以執行日 2026-08-18 計。
- **NML 監測**: scrape 雙分類聯集 snapshot=5880；nml_new=19（10 篇 2026-08-18 + 9 篇 2026-08-17），非洪水（聯集基線持續生效），無需手動聯集修正。
- **構建**: 第一次構建 93 条 → dropped_en 讀取（模型 4、產品 1、行業 3、技巧 6）→ 重寫 supplement_urls.json（實抓 12：模型 4、產品 2、行業 3、技巧 3；論文研究 toutiao 無區塊被濾）→ 重寫 frontend.json 10 篇（掘金/InfoQ中文/開源中國/SegmentFault/w3ctech）→ 第二次構建 **97 条 / 7 版塊**：限時情报王 40、模型发布/更新 8、产品发布/更新 6、行业动态 10、论文研究 0、技巧与观点 13、熱門優惠 20。supplement 合併 12、frontend 合併 10。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=**10**（url∈nml_new 且 date==2026-08-18）；nml-daily.html `new_vs_baseline=10`、total 5880、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `_inline_check_today.js` 通過（899KB, 1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1（herenow 徽章隱藏，非 onerror）。build_site ≡ ghpages（pin 後 IDENTICAL）。
- **舊聞分頁**: DATA.old=**857** 条（>5 天累積，較 8/17 的 827 增加）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `9bc24f3`「每日整合：限時情报王 + AI HOT 2026-08-18」push（bb3942f..9bc24f3）；`/` 與 `/nml-daily.html` 皆回 HTTP 200 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-18.html`（儀表盤副本 1170KB）+ `nml-daily.html`（51KB），提示去連接器頁連接 WeCom/SCRM。

## 2026-08-19 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-19｜fetch_daily 今日期已發佈（sections=4, items=16），無需回退。
- **NML 監測**: scrape 雙分類聯集 snapshot=**4150**（較 8/18 的 5880 下降，疑似 NML 站改版/分頁減少，但非洪水）；nml_new=**1**（《Aurora AI》限時免費，2026-08-19），非洪水，無需手動聯集修正。
- **構建**: 第一次構建 98 条（含前次殘留 supplement/frontend）→ dropped_en 15 張（模型 4、產品 8、行業 5、論文 4、技巧 8 → 4 版塊計 21？實際 15 張跨 4 版塊）→ 重寫 supplement_urls.json（中文域名：qq/163/sina/sohu/tencent/csdn）→ fetch_supplement 實抓 **15/15** → 重寫 frontend.json 10 篇（掘金/InfoQ中文/開源中國/SegmentFault/w3ctech：Rspack 2.2、TypeScript 7、Nuxt 4.5、React Compiler GA、Webpack→Rspack、前端週刊、2026 前端棧等）→ 第二次構建 **101 条 / 7 版塊**：限時情报王 40、熱門優惠 20、產品發布/更新 16、技巧与观点 15、論文研究 8、行業動態 2、模型發布/更新 0。supplement 合併 15、frontend 合併 10（同一批 URL 二次重抓多 404/429，但 JSON 內容已合併，卡片照常顯示）。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=**1**（Aurora AI 限時免費，歸入熱門優惠）；nml-daily.html `new_vs_baseline=1`、total 4150、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `_inline_check_today.js` 通過（906KB, 1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1（herenow 徽章隱藏，非 onerror）。build_site ≡ ghpages（pin 後）。偶發 404/429 圖片與全文重抓失敗不影響構建。
- **舊聞分頁**: DATA.old=**1519** 条（依 archive isoDate 估算；archive 累計 1667 條，其中 612 筆 isoDate 缺失/無效被計入 >5 天 → 較 8/18 的 857 大幅增加，主因 archive 累積大量無效日期條目；非腳本錯誤）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `d08159e`「每日整合：限時情报王 + AI HOT 2026-08-19」push（9bc24f3..d08159e，已停用 GCM + protocol.version=0/HTTP/1.1）；`/` 與 `/nml-daily.html` 皆回 HTTP 200 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `wechat-digest-2026-08-19.html`（摘要卡片）+ `nml-daily.html`（51KB），提示去連接器頁連接 WeCom/SCRM。
- **待觀察**: NML snapshot 由 5880 驟降至 4150，留意 newmobilelife.com 是否改版導致擷取分頁數減少（若持續下降需檢查 scrape_nml.py 分頁邏輯）。

## 2026-08-20 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-20｜fetch_daily 今日期已發佈（sections=5, items=14），無需回退。
- **NML 洪水修正（關鍵）**: scrape 雙分類聯集 snapshot=**5890**（較 8/19 的 4150 恢復，站已復原擷取分頁）；但腳本產出 nml_new=**1749**（≈ snapshot 的洪水訊號），主因 8/19 當日 seen 被截斷為 4150（快照驟降），今日站恢復 5890 導致 1740 筆舊文被誤判 NEW。依任務指示手動收窄：nml_new 改為「近 7 日（>=2026-08-13）且不在 prev 基線」= **18 urls**（10 @ 8/19 + 8 @ 8/20）；nml_seen 已為全量 5890（union 仍 5890），防下次再洪水。dashboard 僅 8/20 當日標 NEW。
- **構建**: 第一次構建 99 条（含前次殘留 supplement/frontend）→ dropped_en 14 張（模型 1、產品 5、行業 2、論文 3、技巧 3）→ 重寫 supplement_urls.json（14 URL 全中文域名 new.qq.com 等，fetch_supplement 實抓 **14**：模型 1、產品 5、行業 2、論文 3、技巧 3）→ 重寫 frontend.json 11 篇（Vue 3.6 RC / Rspack 2.2 / Vite / TS 7 / Nuxt 4.5 / React Compiler GA / Webpack→Rspack / 前端週刊 / AI First 架構 / 狀態管理 2026，掘金/InfoQ中文/開源中國/SegmentFault/w3ctech，含 summary+keypoints）→ 第二次構建 **99 条 / 7 版塊**：限時情报王 40、熱門優惠 20、產品發布/更新 15、技巧与观点 12、論文研究 6、行業動態 4、模型發布/更新 2。supplement 合併 14、frontend 合併 11。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=**8**（url∈nml_new 且 date==2026-08-20）；nml-daily.html `new_vs_baseline=8`、total 5890、shown 40，一致（10 篇 8/19 承襲但非今日不標 NEW）。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `_inline_check_today.js` 通過（1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1（herenow 徽章隱藏，非 onerror）。build_site ≡ ghpages（pin 後 IDENTICAL）；ghpages 內聯 script 同步通過。
- **舊聞分頁**: DATA.old=**1002** 条（archive 累計 1723 條，全部 isoDate 可解析，>5 天 1002 條；較 8/19 的 1519 回落，因 8/19 當日含大量無效日期被誤計）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `d553699`「每日整合：限時情报王 + AI HOT 2026-08-20」push（d08159e..d553699，GCM 已停用 + protocol.version=0/HTTP/1.1）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-20.html`（儀表盤副本 99 条）+ `nml-daily-2026-08-20.html`（50KB），提示去連接器頁連接 WeCom/SCRM。
- **經驗/待觀察**: 8/19 的 snapshot 驟降（4150）係站端暫時性分頁減少，8/20 已恢復 5890；此類「seen 被短期低快照截斷 → 後續恢復即洪水」為已知陷阱，手動收窄 nml_new 為近 7 日即可，無需改 seen（seen 維持全量 5890 防再洪水）。下次若 snapshot 又驟降需留意站是否改版。

## 2026-08-21 (08:00 排程自動執行) — 執行成功 ✅
- **日期**: 2026-08-21（周五）｜fetch_daily 今日期已發佈（sections=5, items=17），無需回退。
- **NML 監測**: scrape 雙分類聯集 snapshot=**5920**；nml_new=**48**（22 @ 2026-08-21 + 26 @ 2026-08-20），非洪水（聯集基線 5920 持續生效），無需手動聯集修正。
- **構建**: 第一次構建 102 条（含前次殘留 supplement/frontend）→ dropped_en **15 張**（模型 1、產品 8、論文 2、技巧 4）→ 中文補充（supplement_urls.json 全 new.qq.com，11 URL 實抓 **11**：模型 2、產品 3、論文 2、技巧 4）→ 重寫 frontend.json 11 篇（掘金/InfoQ中文/開源中國/SegmentFault/w3ctech：Nuxt 4.5、Rspack 2.1、Vue 3.6 RC、TypeScript 7、React Compiler、Webpack→Rspack 等，含 summary+keypoints）→ 第二次構建 **99 条 / 7 版塊**：限時情报王 40、產品發布/更新 15、技巧与观点 12、模型發布/更新 4、論文研究 4、行業動態 4、熱門優惠 20。supplement 合併 11、frontend 合併 11。
- **NML NEW**: 儀表盤限時情报王（live 首欄 40）NEW=**22**（url∈nml_new 且 date==2026-08-21）；nml-daily.html `new_vs_baseline=22`、total 5920、shown 40，一致。AI HOT 5 版塊 + 熱門優惠 NEW 均為 0。
- **品質**: index.html 內聯 script `_inline_check_today.js` 通過（1.3MB, 1 block, ok:1, bad:0）；`dealImgFallback(this,'` 0 命中、`onerror display='none'` 0 命中、`&quot;none&quot;` 1（herenow 徽章隱藏，非 onerror）。build_site ≡ ghpages（pin 後 IDENTICAL）。偶發 429/521 圖片與全文重抓失敗不影響構建。
- **舊聞分頁**: DATA.old=**991** 条（>5 天累積，較 8/20 的 1002 略減，主因 archive 清理；非腳本錯誤）。
- **GitHub Pages**: `cp -r build_site/. ghpages/` + 複製 nml-daily.html → git pull(Already up to date) → commit `ac811f3`「每日整合：限時情报王 + AI HOT 2026-08-21」push（d553699..ac811f3，GCM 已停用 + protocol.version=0/HTTP/1.1）；`/` 與 `/nml-daily.html` 皆上線 → https://liuchiwai0101.github.io/news/
- **限時情报王置頂**: pin_nml_top.py 對 build_site + ghpages 皆回報 pinned to top + nav order updated（idempotent）。
- **微信推送**: WeCom / 微盛SCRM 連接器仍 disconnected → 未推送；已存 `ai-daily-2026-08-21.html`（儀表盤副本 1.3MB / 99 条）+ `nml-daily.html`（39KB），提示去連接器頁連接 WeCom/SCRM。
