from pydub import AudioSegment

def split_audio(input_file, output_dir, segment_length=5000):
    # 음성 파일 로드
    audio = AudioSegment.from_wav(input_file)
    
    # 1초 간격으로 분할
    segments = audio[::segment_length]
    
    # 각 세그먼트 저장
    for i, segment in enumerate(segments):
        output_path = f"{output_dir}/segment_{i}.wav"
        segment.export(output_path, format="wav")

# 입력 파일 경로와 출력 디렉토리 경로 지정
input_file = "new_plastic.wav"
output_dir = "./반복/plastic"

# 음성 파일 분할 및 저장
split_audio(input_file, output_dir)