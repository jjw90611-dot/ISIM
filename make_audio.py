import asyncio
import edge_tts
from pydub import AudioSegment
import os

# ==========================================
# 1. 문제 데이터 (db_info.py에 있는 내용과 동일하게 맞춰주세요)
# ==========================================
QUESTIONS = [
    {"id": 1, "q": "산업안전지도사의 직무에 대해 말해보세요?", "a": "산업안전지도사란 산안법에 따라 사업장 내 근본적인 안전보건상의 문제점을 개선하는데 도움을 받고자 임명한 외부전문가를 말합니다."},
    {"id": 2, "q": "산업안전지도사 기계분야의 직무에 대해 말해보세요?", "a": "산안법 제145조 제1항에 따라 등록한 기계안전지도사의 업무범위는 유해위험방지계획서, 안전보건개선계획서 작성 지도 등이 있습니다."},
    # 필요한 만큼 문제를 추가하세요.
]

# ==========================================
# 2. TTS 설정
# ==========================================
VOICE_Q = "ko-KR-InJoonNeural" # 질문 (남성 목소리)
VOICE_A = "ko-KR-SunHiNeural"  # 답변 (여성 목소리)
OUTPUT_DIR = "audio_files"     # 저장될 폴더 이름

# 폴더가 없으면 자동 생성
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 음성 생성 함수
async def generate_audio(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

# 메인 실행 함수
async def main():
    all_audio = AudioSegment.empty() # 전체 듣기용 빈 오디오 객체

    print("🎙️ 음성 파일 생성을 시작합니다...\n")

    for item in QUESTIONS:
        q_id = item["id"]
        
        # TTS가 자연스럽게 읽도록 텍스트 다듬기
        q_text = f"질문 {q_id}번. {item['q']}"
        a_text = f"답변. {item['a']}"
        
        q_file = f"{OUTPUT_DIR}/temp_q_{q_id}.mp3"
        a_file = f"{OUTPUT_DIR}/temp_a_{q_id}.mp3"
        final_file = f"{OUTPUT_DIR}/qna_{q_id}.mp3"
        
        print(f"⏳ [{q_id}번 문제] 생성 중...")
        
        # 1. 질문과 답변 각각 MP3 생성
        await generate_audio(q_text, VOICE_Q, q_file)
        await generate_audio(a_text, VOICE_A, a_file)
        
        # 2. 두 파일 합치기 (질문과 답변 사이에 1초 쉬는 시간 추가)
        audio_q = AudioSegment.from_mp3(q_file)
        audio_a = AudioSegment.from_mp3(a_file)
        silence_1s = AudioSegment.silent(duration=1000) # 1초(1000ms) 묵음
        
        combined = audio_q + silence_1s + audio_a
        combined.export(final_file, format="mp3")
        
        # 3. 전체 듣기 파일에 추가 (다음 문제로 넘어가기 전 2초 쉬기)
        silence_2s = AudioSegment.silent(duration=2000)
        all_audio += combined + silence_2s
        
        # 4. 임시 파일(개별 질문/답변) 삭제
        os.remove(q_file)
        os.remove(a_file)
        
        print(f"✅ [{q_id}번 문제] 완료!")

    # 전체 듣기 파일 저장
    all_file_path = f"{OUTPUT_DIR}/all_qna.mp3"
    all_audio.export(all_file_path, format="mp3")
    
    print(f"\n🎉 모든 작업이 완료되었습니다!")
    print(f"📁 '{OUTPUT_DIR}' 폴더를 확인해보세요.")

if __name__ == "__main__":
    asyncio.run(main())
