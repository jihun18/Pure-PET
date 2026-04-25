import time
from adafruit_servokit import ServoKit

# 16채널 PCA9685 객체 초기화
kit = ServoKit(channels=16)

# 사용할 서보 객체 정의 (0, 1, 2번 채널)
servos = [kit.servo[0], kit.servo[1], kit.servo[2]]

print("3채널 서보 모터 테스트를 시작합니다.")
print("5V 5A 외부 전원이 연결되었는지 확인하세요.")

def move_servos(angle):
    """3개의 서보를 동시에 지정된 각도로 이동"""
    print(f"모든 서보를 {angle}도로 이동 중...")
    for s in servos:
        s.angle = angle

try:
    while True:
        # 1. 순차적 이동 테스트
        for i, s in enumerate(servos):
            print(f"{i}번 서보: 0도")
            s.angle = 0
            time.sleep(0.5)
            print(f"{i}번 서보: 90도")
            s.angle = 90
            time.sleep(0.5)

        time.sleep(1)

        # 2. 동시 이동 테스트 (전류 공급 능력 확인)
        move_servos(180)
        time.sleep(1)
        move_servos(0)
        time.sleep(1)
        move_servos(90)
        time.sleep(2)

except KeyboardInterrupt:
    # 종료 시 모든 서보를 안전한 90도 위치로 이동
    print("\n테스트 종료: 모든 서보를 중립(90도)으로 복귀합니다.")
    move_servos(90)
