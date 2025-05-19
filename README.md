# Gemini 語音轉文字應用程式

這是一個使用 Google Gemini API 進行即時語音辨識與翻譯的應用程式。

## 功能特點

- 透過麥克風擷取即時語音
- 將語音傳送至 Gemini API 進行處理
- 接收 API 回傳的文字結果並顯示
- 同時顯示英文原文與繁體中文翻譯
- 支援多種語言翻譯（可選）：
  - 日文
  - 韓文
  - 越南文
  - 泰國文
  - 西班牙文
  - 法文
  - 德文

## 安裝步驟

### 1. 安裝 PortAudio (Mac 環境必須)

在 Mac 上，安裝 PyAudio 之前必須先安裝 PortAudio 庫：

```bash
brew install portaudio
```

如果您沒有安裝 Homebrew，請先安裝：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 創建虛擬環境 (建議)

```bash
python -m venv myenv
source myenv/bin/activate  # Mac/Linux
# 或者在 Windows 上：
# myenv\Scripts\activate
```

### 3. 安裝 PyAudio

在 Mac 上，使用以下命令安裝 PyAudio：

```bash
pip install --global-option='build_ext' --global-option='-I/opt/homebrew/include' --global-option='-L/opt/homebrew/lib' pyaudio
```

如果上述命令失敗，請嘗試：

```bash
pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio
```

### 4. 安裝其他依賴

```bash
pip install websockets python-dotenv
```

或者直接使用修改後的 requirements.txt：

```bash
pip install -r requirements.txt
```

## 設定

1. 複製 `.env.example` 檔案為 `.env`：

```bash
cp .env.example .env
```

2. 編輯 `.env` 檔案，填入您的 Gemini API key 並設定語言支援：

```
# API 設定
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# 語言支援設定 (true/false)
# 設定為 true 以啟用對應語言的翻譯
ENABLE_JAPANESE=false
ENABLE_KOREAN=false
ENABLE_VIETNAMESE=false
ENABLE_THAI=false
ENABLE_SPANISH=false
ENABLE_FRENCH=false
ENABLE_GERMAN=false
```

若要啟用特定語言的翻譯，請將對應的設定值改為 `true`，例如：

```
ENABLE_JAPANESE=true
ENABLE_FRENCH=true
```

## 使用方法

執行應用程式：

```bash
python app.py
```

開始說話，應用程式會將您的語音轉換為文字，並在偵測到英文語音時同時顯示英文原文與您所啟用的語言翻譯。

預設情況下，應用程式會顯示繁體中文翻譯。如果您啟用了其他語言，則會同時顯示這些語言的翻譯。

## 故障排除

如果在安裝 PyAudio 時遇到問題，請確保：

1. 已正確安裝 PortAudio 庫
2. 使用了正確的編譯選項，指向 PortAudio 的安裝位置
3. 如果使用 Apple Silicon Mac (M1/M2/M3)，可能需要額外的設定

## 系統需求

- Python 3.7 或更高版本
- 麥克風
- 網際網路連線
- Gemini API 金鑰