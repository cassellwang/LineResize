"# LineResize

LINE 貼圖尺寸轉換工具 - 批次將圖片轉換為 370x320 PNG 格式

## 功能特色

- **保持比例**：圖片不會被拉伸變形
- **自動補邊**：自動填充透明區域達到 370x320 尺寸
- **背景移除**：可自動偵測角落顏色或手動指定背景色
- **軟邊效果**：移除背景時產生漸層透明效果，邊緣更自然
- **支援格式**：PNG、JPG、JPEG、WEBP、BMP、GIF

## 安裝依賴

首先安裝必要的 Python 套件：

```powershell
py -m pip install -r requirements.txt
```

## 執行方法

### 基本轉換（保持原背景）
```powershell
py line_sticker_resize.py input --output out_370x320
```

### 進階轉換（移除背景，產生透明背景）
```powershell
py line_sticker_resize.py input --output out_back_370x320 --make-transparent --tolerance 18
```

### 指定背景顏色移除
```powershell
py line_sticker_resize.py input --output out_370x320 --make-transparent --bg-color #FFFFFF --tolerance 18
```

## 參數說明

- `input`：輸入資料夾或單一圖片檔案
- `--output` 或 `-o`：輸出資料夾（預設為 `output_370x320`）
- `--make-transparent`：嘗試移除純色背景並產生透明背景
- `--bg-color`：指定要移除的背景顏色（16進位，如 `#FFFFFF`）
- `--tolerance`：顏色容差值（0-64，預設 18）

## 使用範例

```powershell
# 基本轉換
py line_sticker_resize.py input

# 指定輸出資料夾
py line_sticker_resize.py input --output my_stickers

# 移除白色背景
py line_sticker_resize.py input --make-transparent --bg-color #FFFFFF

# 自動偵測背景色並移除
py line_sticker_resize.py input --make-transparent --tolerance 25
```

## 專案結構

```
LineResize/
├── line_sticker_resize.py  # 主程式
├── requirements.txt        # 依賴套件
├── README.md              # 說明文件
├── input/                 # 輸入圖片資料夾
└── out_370x320/          # 輸出圖片資料夾
```

## 執行結果

程式會處理輸入資料夾中的所有圖片，轉換後的檔案會儲存在輸出資料夾中：
- 統一轉換為 PNG 格式
- 尺寸調整為 370x320 像素
- 保持原圖比例，空白處填充透明背景
- 可選擇移除背景色，產生透明效果" 
