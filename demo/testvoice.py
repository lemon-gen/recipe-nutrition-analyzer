import asyncio
import edge_tts
import pygame
from pathlib import Path
import os

class EdgeTTS:
    def __init__(self):
        self.voices = {
            'zh-CN-XiaoxiaoNeural': '中文女 (晓晓)',
            'zh-CN-YunxiNeural': '中文男 (云希)',
            'zh-CN-XiaoyiNeural': '中文女 (晓伊)',
            'zh-CN-YunyangNeural': '中文男 (云扬)',
            'en-US-JennyNeural': '英文女 (Jenny)',
            'en-US-GuyNeural': '英文男 (Guy)',
        }

    def read_text_from_file(self, txt_path="input.txt"):
        """从 TXT 文件读取文本（自动处理编码）"""
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()
            if not text.strip():
                print("❌ TXT 文件内容为空！")
                return None
            print(f"✅ 成功从文件读取文本：{txt_path}")
            return text
        except FileNotFoundError:
            print(f"❌ 未找到文件：{txt_path}，请创建 input.txt 并写入内容")
            return None
        except Exception as e:
            print(f"❌ 读取文件失败：{str(e)}")
            return None

    async def generate(self, text, voice='en-US-JennyNeural',
                       output_file='output.mp3'):
        """异步生成语音文件"""
        if not text or not text.strip():
            print("❌ 文本不能为空！")
            return None

        communicate = edge_tts.Communicate(text, voice)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        await communicate.save(output_file)
        print(f"✅ 音频已保存: {os.path.abspath(output_file)}")
        return output_file

    def play(self, audio_file):
        """播放音频文件"""
        if not Path(audio_file).exists():
            print(f"❌ 音频文件不存在: {audio_file}")
            return

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            print("🔊 开始播放音频...")

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            print("✅ 播放完成！")
        except Exception as e:
            print(f"❌ 播放失败: {str(e)}")
        finally:
            pygame.mixer.music.stop()
            pygame.mixer.quit()


async def main():
    tts = EdgeTTS()

    text = tts.read_text_from_file(txt_path="recipe_result.txt")
    if not text:
        return

    audio_path = await tts.generate(
        text=text,
        voice="en-US-JennyNeural", 
        output_file="output/tts_output.mp3"
    )

    if audio_path:
        tts.play(audio_path)


if __name__ == "__main__":
    asyncio.run(main())
