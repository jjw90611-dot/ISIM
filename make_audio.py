import asyncio
import edge_tts
from pydub import AudioSegment
import os

async def create_qna_audio(question_text, answer_text, file_name):
    # 1. 질문 생성 (남성 목소리: InJoon)
    communicate_q = edge_tts.Communicate(f"질문입니다. {question_text}", "ko-KR-InJoonNeural")
    await communicate_q.save("temp_q.mp3")
    
    # 2. 답변 생성 (여성 목소리: SunHi)
    communicate_a = edge_tts.Communicate(f"답변입니다. {answer_text}", "ko-KR-SunHiNeural")
    await communicate_a.save("temp_a.mp3")
    
    # 3. 두 오디오 파일 병합 (질문 -> 1초 쉬고 -> 답변)
    audio_q = AudioSegment.from_mp3("temp_q.mp3")
    audio_a = AudioSegment.from_mp3("temp_a.mp3")
    silence = AudioSegment.silent(duration=1000) # 1초 묵음
    
    combined = audio_q + silence + audio_a
    combined.export(file_name, format="mp3")
    
    # 임시 파일 삭제
    os.remove("temp_q.mp3")
    os.remove("temp_a.mp3")
    print(f"✅ {file_name} 생성 완료!")

# 실행 예시 (비동기 실행)
async def main():
    # 실제 DB 데이터를 반복문으로 돌리시면 됩니다.
    await create_qna_audio(
        "기계설비의 위험점 6가지는 무엇입니까?", 
        "협착점, 끼임점, 절단점, 물림점, 접선물림점, 회전말림점 입니다.", 
        "qna_1.mp3"
    )

if __name__ == "__main__":
    asyncio.run(main())
