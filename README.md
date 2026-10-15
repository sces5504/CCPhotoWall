# CCPhotoWall

[![GitHub Pages](https://github.com/sces5504/CCPhotoWall/actions/workflows/pages.yml/badge.svg)](https://github.com/sces5504/CCPhotoWall/actions/workflows/pages.yml)

一個可以自行挑選、管理與分享的個人照片牆。透過 GitHub 上傳圖片、發布隱藏名單，就能維護所有訪客看到的同一份圖片庫。

[瀏覽照片牆](https://sces5504.github.io/CCPhotoWall/) · [開啟管理頁](https://sces5504.github.io/CCPhotoWall/admin.html) · [查看部署狀態](https://github.com/sces5504/CCPhotoWall/actions)

## 功能特色

- **三欄照片牆**：正方形裁切、置中排列，支援電腦與手機瀏覽。
- **大圖檢視**：點開照片查看大圖，支援箭頭按鈕與鍵盤切換；手機保留原生縮放，不使用左右滑動換圖。
- **批次管理**：單張或多張照片都能隱藏、恢復，其他照片依序補位。
- **統一發布**：發布後所有訪客使用相同的隱藏名單，草稿可先預覽、匯出與匯入。
- **上傳即更新**：圖片提交到 GitHub 後，自動產生清單並部署至 GitHub Pages。
- **靜態網站**：使用 HTML、CSS 與原生 JavaScript，無需資料庫或 API 金鑰；建置只需要 Python 標準函式庫。

## 快速上手：上傳自己的照片

如果你要更新目前這個專案，直接使用管理頁的「新增照片」入口。若要建立自己的照片牆，先完成下一節的 Fork 與部署設定。

1. 開啟你的 repo，進入 `assets/photos/`。
2. 選擇 **Add file → Upload files**，將圖片拖入上傳區。
3. 按 **Commit changes**，提交到 `main` 分支。
4. 等待 Actions 中的 **Publish photo wall** 執行成功，再重新整理網站。

也可以從管理頁按「新增照片」前往上傳頁。新增圖片會排在照片牆最前面，已發布的隱藏名單會保留。

### 圖片與命名規則

| 項目 | 說明 |
| --- | --- |
| 支援格式 | JPG、JPEG、PNG、WebP、GIF、AVIF |
| 放置位置 | 直接放在 `assets/photos/`，不要再建立子資料夾 |
| 檔名 | 建議使用 `2026-10-15-01.jpg` 這類日期加編號的名稱 |
| 唯一識別 | 去掉副檔名後必須唯一，例如 `photo-01.jpg` 與 `photo-01.png` 不能同時存在 |
| 新照片排序 | 依檔名反向排序；以日期開頭，可讓較新的照片排在前面 |
| 圖片壓縮 | 上傳流程不會自動縮圖或壓縮，請先準備適合網站瀏覽的圖片 |

一般使用只需要上傳一份圖片，列表與大圖檢視都會使用它。大量圖片可改用 Git 提交，避免逐批透過網頁上傳。

### 分別提供縮圖與大圖（選用）

若想兼顧載入速度與放大細節，可以準備兩個檔案：

```text
assets/photos/2026-10-15-01.jpg     # 照片牆使用的縮圖
assets/large/2026-10-15-01.webp     # 點開照片後使用的大圖
```

兩個檔案的名稱主體必須相同。`assets/large/` 目前只會配對 `.webp` 檔案；沒有對應大圖時，檢視器會使用 `assets/photos/` 裡的圖片。大圖載入失敗時也會退回列表圖。

## 建立自己的圖片庫

### 1. Fork 專案

在本專案頁面點選 **Fork**，建立到自己的 GitHub 帳號。之後請在自己的 repo 上傳圖片與修改設定。

Fork 會包含目前的示範照片。你可以保留它們繼續新增，也可以依下一步清空，改用自己的圖片庫。

### 2. 換成自己的照片

若要完全移除示範照片，建議在電腦上處理。先將自己的 Fork 複製到本機，將下面的帳號與 repo 名稱換成你的設定：

```sh
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

以下指令會從目前工作目錄的圖片庫移除既有圖片，並重設排序資料與隱藏名單。請在自己的副本執行，並先備份已經放入的個人圖片；若要保留示範照片，可跳過這組指令。

```sh
git rm -r --ignore-unmatch assets/photos assets/large
mkdir -p assets/photos

python3 - <<'PY'
import json
from pathlib import Path

Path("data/catalog.json").write_text(
    json.dumps({"version": 1, "photos": [], "rows": []}, indent=2) + "\n",
    encoding="utf-8",
)
Path("data/visibility.json").write_text(
    json.dumps({"version": 1, "hidden": []}, indent=2) + "\n",
    encoding="utf-8",
)
PY
```

接著把自己的圖片複製到 `assets/photos/`。保留空白的 `catalog.json` 即可，建置時會自動掃描圖片，不需要手動建立照片清單。

清空以上檔案只會更新目前版本的圖片庫，Fork 的 Git 歷史仍會保留既有提交。

### 3. 調整管理頁連結

目前 `admin.html` 的 GitHub 入口指向本專案。請將這兩個連結改為自己的 repo：

| 入口 | 改成 |
| --- | --- |
| 新增照片 | `https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/upload/main/assets/photos` |
| 上傳名單 | `https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/upload/main/data` |

請在 `admin.html` 搜尋 `https://github.com/sces5504/CCPhotoWall/` 並替換成自己的 repo 路徑。

你也可以在 `index.html`、`admin.html` 修改網站名稱與頁面標題，讓照片牆使用自己的名稱。

### 4. 本機預覽與提交

安裝 Python 3 與 Git 後，在專案根目錄執行：

```sh
python3 scripts/build.py
python3 -m http.server 4173 --directory dist
```

開啟 <http://localhost:4173/>；管理頁位於 <http://localhost:4173/admin.html>。結束預覽時，在終端機按 `Ctrl+C`。

確認照片與管理頁連結正常後，提交到自己的 repo：

```sh
git add assets data admin.html index.html
git commit -m "Set up my photo library"
git push origin main
```

`dist/` 是自動產生的部署產物，不需要提交。之後每次更動圖片或設定，請重新執行 `python3 scripts/build.py`，再檢查本機預覽。

### 5. 啟用 GitHub Pages

1. 在自己的 repo 開啟 **Settings → Pages**。
2. 將 **Build and deployment → Source** 設為 **GitHub Actions**。
3. 若 Fork 的 Actions 尚未啟用，先到 **Actions** 頁面允許執行工作流程。
4. 推送到 `main`，或在 **Actions → Publish photo wall → Run workflow** 手動觸發部署。
5. 等待 `build` 與 `deploy` 都成功，使用部署結果提供的網址開啟網站。

一般專案網址為：

```text
https://YOUR_USERNAME.github.io/YOUR_REPOSITORY/
```

本專案已附上部署流程，無需另外新增 GitHub 提供的網站範本。設定方式可參考 [GitHub Pages 官方文件](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

## 管理隱藏名單

### 選取、預覽與發布

1. 開啟 `admin.html`，勾選照片，按「隱藏選取照片」。
2. 需要恢復時，切到「已隱藏」列表，選取照片並按「恢復選取照片」。
3. 按「預覽照片牆」，確認尚未發布的草稿。
4. 按「下載隱藏名單」，取得 `visibility.json`。
5. 按「上傳名單」，登入有 repo 寫入權限的 GitHub 帳號，把檔案上傳至 `data/`，覆蓋原本的同名檔案。
6. 提交到 `main`，等待部署成功。所有訪客就會看到更新後的照片牆。

若瀏覽器把下載檔案改名為 `visibility (1).json`，請先改回 **`visibility.json`** 再上傳。

### 草稿與發布權限

管理頁的草稿保存在目前裝置，可下載備份或匯入既有名單。操作草稿不會直接改變公開網站；新版名單發布後，與舊版設定不符的裝置草稿會失效。

管理頁不保存 GitHub 存取金鑰。發布權限由 GitHub repo 的寫入權限決定；其他訪客在自己瀏覽器進行的選擇，不會改動你的照片牆。

### 隱藏與刪除的差別

隱藏會從照片牆移除圖片的位置，後面的照片依原順序補位；同一張照片重複出現時，會一起隱藏。圖片檔案仍保留，日後可以恢復，也可能透過直接網址或公開 repo 存取。

`data/catalog.json` 記錄示範庫的既有照片與每列分組。若保留這份資料，請用管理頁隱藏照片；直接刪除它引用的圖片會使建置失敗。建立完全獨立的圖片庫時，請依前面的步驟重設這份資料。

## 專案結構

```text
CCPhotoWall/
├── index.html                   # 公開照片牆
├── admin.html                   # 選取、預覽與匯出名單
├── gallery.js                   # 共用清單處理與大圖檢視
├── wall.js                      # 公開頁與草稿預覽
├── admin.js                     # 管理頁操作與本機草稿
├── style.css / admin.css        # 頁面樣式
├── assets/
│   ├── photos/                  # 上傳圖片或列表縮圖
│   └── large/                   # 選用的大圖（同名 WebP）
├── data/
│   ├── catalog.json             # 既有照片順序與分組；新圖片庫可留空
│   └── visibility.json          # 對所有訪客生效的隱藏名單
├── scripts/build.py             # 驗證資料、產生清單與部署目錄
├── .github/workflows/pages.yml  # GitHub Pages 自動部署
└── dist/                        # 建置產物，不納入版本控制
```

建置流程會掃描圖片、驗證檔名與資料，再產生 `dist/data/photos.json`。一般新增圖片時，不需要手動編輯產生的照片清單。

## 常見問題

**上傳後沒有看到新圖片？**

確認檔案直接放在 `assets/photos/`，已提交到 `main`，且 Actions 最近一次部署成功。重新整理頁面，避免繼續看到瀏覽器快取的版本。

**Fork 後，新增照片或上傳名單卻開到原專案？**

請修改 `admin.html` 的 GitHub 上傳連結，指向自己的帳號與 repo。

**建置提示檔名重複？**

檔名不含副檔名的部分就是照片 ID。同時存在 `trip.jpg` 與 `trip.png` 時，請重新命名其中一張。

**下載名單後，其他人看到的照片沒有變？**

下載只會產生設定檔。還需要將它上傳到 `data/visibility.json`，提交並完成部署。

**照片點開後還是模糊？**

請確認上傳檔案本身的解析度。一般圖片會直接作為大圖使用；若有另外準備縮圖，請將較清楚的同名 `.webp` 放進 `assets/large/`。網站不會替圖片人工補出細節。
