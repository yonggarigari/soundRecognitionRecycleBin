import pyaudio
import numpy as np
import wave


def detect_sound(duration, threshold):
    frames = []
    sound_detected = False
    while not sound_detected:
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

            # 소리 감지 로직
            audio_data = np.frombuffer(data, dtype=np.int16)
            if np.abs(audio_data).mean() > threshold:
                print("* Sound detected!")
                sound_detected = True
                break

    return sound_detected

def record_audio(duration):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* Recording...")

    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    #audio_data = b''.join(frames)

    #output_filename = "recorded_audio.wav"

    #with wave.open(output_filename, 'wb') as wf:
    #    wf.setnchannels(CHANNELS)
    #    wf.setsampwidth(p.get_sample_size(FORMAT))
    #    wf.setframerate(RATE)
    #    wf.writeframes(audio_data)



    return b''.join(frames)

def play_audio(audio_data):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=48000,
                    output=True)

    print("* Playing recorded audio...")

    stream.write(audio_data)

    print("* Playback finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    duration = 1  # 녹음할 시간 (초)
    threshold = 15000  # 소리 감지 임계값 (값은 조정 가능)

    while True:
        #audio_data = record_audio(duration)
        if detect_sound(duration, threshold):
            audio_data = record_audio(duration)
            play_audio(audio_data)
