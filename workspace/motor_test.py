import subprocess
import RPi.GPIO as GPIO
import time

# 서브프로세스 경로 
stepMotor_script_path = "step_motor.py"

# GPIO 핀 번호 설정
proximity_sensor = 14
relay_pin = 15

# GPIO 핀 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.setup(proximity_sensor, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

# 쓰레기통 딕셔너리
others_dict = {
    'others':0,
    'can':1,
    'paper':2,
    'plastic':3
}

can_dict = {
	'can':0,
	'paper':1,
	'plastic':2,
	'others':3
}

paper_dict = {
	'paper':0,
	'plastic':1,
	'others':2,
	'can':3
}

plastic_dict = {
	'plastic':0,
	'others':1,
	'can':2,
	'paper':3
}


current_bin = 'others'
target_bin = 'others'

def rotating_90():
	GPIO.output(relay_pin, GPIO.HIGH)
	time.sleep(1)
	while True:
		if GPIO.input(proximity_sensor)==GPIO.HIGH:
			GPIO.output(relay_pin, GPIO.LOW)
			break

def dist_(current_bin, target_bin):
	if current_bin == 'others':
		current_dict = others_dict
	elif current_bin == 'can':
		current_dict = can_dict
	elif current_bin == 'paper':
		current_dict = paper_dict
	elif current_bin == 'plastic':
		current_dict = plastic_dict

	distance = abs(current_dict[current_bin] - current_dict[target_bin])
	return distance

def rotating_bin(distance):
	for _ in range(distance):
		rotating_90()
	subprocess.run(["python3",stepMotor_script_path])

#try:
    #while True:
    	#target_bin = input("어떤 쓰레기?")
    	#rotating_bin(dist_(current_bin, target_bin))
    	#current_bin = target_bin
    	#print(current_bin)
    	#print(target_bin)
#except KeyboardInterrupt:
    # 프로그램 종료 시 GPIO 리소스 정리
    #GPIO.cleanup()

