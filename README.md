# CCPhotoWall

照片牆：https://sces5504.github.io/CCPhotoWall/

管理頁：https://sces5504.github.io/CCPhotoWall/admin.html

重現來源微博圖片牆的置中三欄、正方形裁切、照片順序與原本的每列分組。已匯入來源頁目前載入的 **1,591 張不同照片**；原頁三張重複顯示的照片也保留在其原本位置（共 1,594 個位置、556 列）。

圖片已存入 repo，由 GitHub Pages 託管。來源頁提供的圖片是 `orj480` 預覽版本；未取得或宣稱具有原始全尺寸圖檔。

## 隱藏、恢復與發布

1. 開啟管理頁，勾選單張或多張照片，按「隱藏選取照片」。
2. 在「已隱藏」列表選取照片，按「恢復選取照片」，即可恢復。
3. 按「預覽照片牆」確認結果；這是尚未發布的草稿。
4. 按「下載隱藏名單」，取得 `visibility.json`。
5. 按「上傳名單」，登入 **sces5504** 的 GitHub 帳號，把檔案拖入 `data/`，覆蓋原本的 `visibility.json`，按 **Commit changes** 提交到 main 分支。若瀏覽器替檔名加上「(1)」，先改回 `visibility.json`。
6. 等待 [Actions](https://github.com/sces5504/CCPhotoWall/actions) 的「Publish photo wall」成功。重新整理網站後，所有訪客會看到相同名單。

隱藏照片時，後面的照片會按原順序補位。重複出現的同一張照片會一起隱藏。管理頁的草稿會保存在目前裝置，不會自動發布；新發布名單會取代已過期的裝置草稿。可下載名單备份或匯入既有檔案。

管理頁不持有 GitHub 存取金鑰，也不能直接修改線上資料。訪客即使在自己的瀏覽器操作管理頁，也無法發布你的 repo。發布權限由 GitHub 的 repo 權限決定。

「隱藏」只影響照片牆的顯示，檔案保留以便恢復；公開 repo 和圖片直接網址仍能存取圖檔。

## 新增照片

1. 在管理頁按「新增照片」，或開啟 [照片資料夾上傳頁](https://github.com/sces5504/CCPhotoWall/upload/main/assets/photos)。
2. 把照片拖入上傳頁，按 **Commit changes** 提交到 main 分支。
3. 等待 Actions 部署完成。新增照片會自動出現在照片牆最前面，原有的隱藏紀錄保留。

支援 JPG、JPEG、PNG、WebP、GIF、AVIF。直接放在 `assets/photos/`，不用手動編輯清單。請使用不同的檔名（不含副檔名的部分也要不同），例如 `2026-10-15-01.jpg`。新照片依檔名反向排序；以日期開頭可讓較新的排在前面。不要刪除原本的匯入圖片；若不想顯示，請用管理頁隱藏。

## 本機預覽

```sh
python3 scripts/build.py
python3 -m http.server 4173 --directory dist
```

開啟 `http://localhost:4173/`。建置只使用 Python 標準函式庫，網站不需要伺服器、資料庫或 API 金鑰。

來源：[微博圖片牆](https://m.weibo.cn/p/second?containerid=1078037295705281_-_photoall&page=1&count=24)。匯入內容為 2026-10-15 在 Chrome 中觀察到的已載入照片清單，未自動同步微博新增照片。
