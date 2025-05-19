import asyncio
import base64
import json
import os
import pyaudio
from websockets.asyncio.client import connect
from dotenv import load_dotenv

class GeminiVoiceToText:
    """
    即時語音轉文字類別
    
    這個類別使用 Google Gemini API 來進行即時的語音辨識與翻譯。
    主要功能包括：
    1. 透過麥克風擷取即時語音
    2. 將語音傳送至 Gemini API 進行處理
    3. 接收 API 回傳的文字結果並顯示
    4. 同時顯示英文原文與中文翻譯
    """
    
    def __init__(self):
        """
        初始化方法
        
        設定所有必要的參數與組態：
        1. API 相關設定：存取金鑰、模型版本、WebSocket 連線網址
        2. 音訊設定：取樣格式、聲道數、緩衝區大小、取樣率
        3. Gemini API 的系統指令與回應格式設定
        """
        # 載入 .env 檔案中的環境變數
        load_dotenv()
        
        # Gemini API 設定
        self.api_key = os.environ.get("GEMINI_API_KEY")  # 從環境變數取得 API 金鑰
        if not self.api_key:
            raise ValueError("未設定 GEMINI_API_KEY，請在 .env 檔案中設定")
            
        self.model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")  # 從環境變數取得模型版本，若未設定則使用預設值
        
        # 讀取語言支援設定
        self.enable_japanese = self._parse_bool_env("ENABLE_JAPANESE", False)
        self.enable_korean = self._parse_bool_env("ENABLE_KOREAN", False)
        self.enable_vietnamese = self._parse_bool_env("ENABLE_VIETNAMESE", False)
        self.enable_thai = self._parse_bool_env("ENABLE_THAI", False)
        self.enable_spanish = self._parse_bool_env("ENABLE_SPANISH", False)
        self.enable_french = self._parse_bool_env("ENABLE_FRENCH", False)
        self.enable_german = self._parse_bool_env("ENABLE_GERMAN", False)
        self.uri = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={self.api_key}"  # WebSocket 連線網址
        
        # 音訊錄製設定
        self.FORMAT = pyaudio.paInt16  # 設定音訊格式為 16 位元整數
        self.CHANNELS = 1  # 設定為單聲道錄音
        self.CHUNK = 512  # 每次讀取的音訊區塊大小（位元組）
        self.RATE = 16000  # 取樣率設定為 16kHz，符合語音辨識最佳規格

        # Gemini API 系統組態
        self.config = {
            "setup": {
                "model": f"models/{self.model}",
                "generation_config": {
                    "response_modalities": ["TEXT"]  # 設定 API 回傳格式為純文字
                },
            }
        }

        # 系統指令設定
        self.system_instruction = self._generate_system_instruction()

    def _parse_bool_env(self, key, default=False):
        """解析環境變數中的布林值"""
        value = os.environ.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'y', 't')
    
    def _generate_system_instruction(self):
        """根據語言設定生成系統指令"""
        instruction_text = "When you detect English speech, please respond in this format:\n"
        instruction_text += "First provide the original response in English"
        
        # 添加各種語言的翻譯指令
        translations = []
        
        # 預設添加繁體中文翻譯
        translations.append("then on a new line after '繁體中文：' show the Traditional Chinese (zh-TW) translation. Always use Traditional Chinese characters, not Simplified Chinese")
        
        # 根據設定添加其他語言翻譯
        if self.enable_japanese:
            translations.append("then on a new line after '日本語：' show the Japanese translation")
        
        if self.enable_korean:
            translations.append("then on a new line after '한국어 번역：' show the Korean translation")
        
        if self.enable_vietnamese:
            translations.append("then on a new line after 'Bản dịch tiếng Việt：' show the Vietnamese translation")
        
        if self.enable_thai:
            translations.append("then on a new line after 'การแปลภาษาไทย：' show the Thai translation")
        
        if self.enable_spanish:
            translations.append("then on a new line after 'Traducción al español：' show the Spanish translation")
        
        if self.enable_french:
            translations.append("then on a new line after 'Traduction française：' show the French translation")
        
        if self.enable_german:
            translations.append("then on a new line after 'Deutsche Übersetzung：' show the German translation")
        
        # 組合指令文本
        instruction_text += ", " + ", ".join(translations) + "."
        
        # 返回系統指令
        return {
            "client_content": {
                "turns": [
                    {
                        "parts": [
                            {
                                "text": instruction_text
                            }
                        ],
                        "role": "user"
                    }
                ],
                "turn_complete": True
            }
        }
    
    async def start(self):
        """
        啟動服務的主要方法
        
        功能流程：
        1. 建立與 Gemini API 的 WebSocket 連線
        2. 傳送初始設定與系統指令
        3. 同時啟動兩個非同步任務：
           - 音訊擷取與傳送
           - 文字回應接收與顯示
        
        錯誤處理：
        - 確保所有連線和通訊都有適當的錯誤處理機制
        """
        # 初始化 WebSocket 連線
        async with connect(self.uri) as self.ws:
            # 設定 Content-Type 標頭
            self.ws.request_headers = {"Content-Type": "application/json"}
            
            # 傳送初始組態到 API
            await self.ws.send(json.dumps(self.config))
            await self.ws.recv()

            # 傳送系統指令
            await self.ws.send(json.dumps(self.system_instruction))
            await self.ws.recv()
            print("已連線至 Gemini。您現在可以開始說話...")
            
            # 使用 TaskGroup 同時執行多個非同步任務
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.send_user_audio())  # 啟動音訊傳送任務
                tg.create_task(self.receive_text_responses())  # 啟動回應接收任務

    async def send_user_audio(self):
        """
        音訊擷取與傳送方法
        
        功能說明：
        1. 初始化音訊裝置並開啟麥克風串流
        2. 持續讀取音訊資料
        3. 將音訊資料轉換為 base64 編碼
        4. 透過 WebSocket 傳送至 Gemini API
        
        錯誤處理：
        - 處理音訊裝置異常
        - 確保資源正確釋放
        - 維持連續的音訊串流
        """
        # 初始化音訊系統
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        try:
            while True:
                # 使用非阻塞方式讀取音訊資料
                data = await asyncio.to_thread(stream.read, self.CHUNK)
                # 將音訊資料轉換為 base64 編碼並包裝成 JSON 格式
                await self.ws.send(json.dumps({
                    "realtime_input": {
                        "media_chunks": [{
                            "data": base64.b64encode(data).decode(),
                            "mime_type": "audio/pcm",
                        }]
                    }
                }))
        except Exception as e:
            print(f"音訊串流發生錯誤: {e}")
            # 發生錯誤時進行清理工作
            stream.stop_stream()  # 停止音訊串流
            stream.close()  # 關閉串流
            audio.terminate()  # 終止音訊系統

    async def receive_text_responses(self):
        """
        接收與處理文字回應的方法
        
        功能說明：
        1. 持續監聽來自 Gemini API 的 WebSocket 回應
        2. 解析 JSON 格式的回應資料
        3. 擷取文字內容並進行緩存
        4. 在對話回合結束時顯示完整回應
        
        資料處理：
        - 使用緩存機制收集分段回應
        - 確保回應完整性
        - 格式化輸出結果
        
        錯誤處理：
        - 處理 JSON 解析錯誤
        - 處理資料結構異常
        - 確保程式持續運作
        """
        current_response = ""  # 用於暫存當前回應的文字
        
        async for msg in self.ws:
            try:
                # 解析從 WebSocket 收到的 JSON 訊息
                response = json.loads(msg)
                # 檢查回應是否包含文字內容
                if 'serverContent' in response and 'modelTurn' in response['serverContent']:
                    text_response = response['serverContent']["modelTurn"]["parts"][0].get('text', '')
                    if text_response:
                        current_response += text_response
                    
                # 當一個回應回合完成時顯示結果
                if response['serverContent'].get('turnComplete'):
                    print("\nGemini:", current_response)
                    print("\n-----------------------------------")
                    current_response = ""  # 清空暫存，準備接收下一個回應
                        
            except KeyError as e:
                print(f"回應處理發生錯誤: {e}")
                continue
            except Exception as e:
                print(f"未預期的錯誤: {e}")
                continue

if __name__ == "__main__":
    client = GeminiVoiceToText()
    asyncio.run(client.start())