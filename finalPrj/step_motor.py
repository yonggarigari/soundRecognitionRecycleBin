import RPi.GPIO as GPIO
import time

# 핀 번호 설정
IN1 = 12
IN2 = 16
IN3 = 20
IN4 = 21

# 스텝 시퀀스 정의
step_sequence = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
]

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# 한 스텝 회전 함수
def step(step_sequence, delay):
    for i in range(8):
        for j in range(4):
            GPIO.output(IN1, step_sequence[i][0])
            GPIO.output(IN2, step_sequence[i][1])
            GPIO.output(IN3, step_sequence[i][2])
            GPIO.output(IN4, step_sequence[i][3])
            time.sleep(delay)

# 360도 회전
def rotate_360(degrees, delay):
    steps_per_degree = 512 / 360
    steps = int(degrees * steps_per_degree)
    for _ in range(steps):
        step(step_sequence, delay)

def rotate_360_counter(degrees, delay):
	steps_per_degree = 512/360
	steps = int(degrees * steps_per_degree)
	for _ in range(steps):
		step(list(reversed(step_sequence)), delay)

# 360도 회전 (예시: 1초에 한 스텝씩)
rotate_360(90, 0.0008)
#time.sleep(1)
rotate_360_counter(90, 0.0008)
# GPIO 정리
GPIO.cleanup()
