import time
from adafruit_servokit import ServoKit

# PCA9685 16채널 모듈 초기화
kit = ServoKit(channels=16)

# 지훈님이 새로 확인한 진짜 서보모터 채널 번호
servo_channels = [0, 6, 11]

def init_servos():
    print("=== 모든 서보모터 규격 설정 및 0도 초기화 ===")
    for ch in servo_channels:
        # 대학 프로젝트용 서보모터(SG90, MG90S 등) 표준 펄스 폭 지정
        kit.servo[ch].set_pulse_width_range(500, 2400)
        kit.servo[ch].angle = 0
    time.sleep(2)

def test_sequence():
    print("\n=== 순차적 각도 제어 테스트 시작 ===")
    for ch in servo_channels:
        print(f"\n[채널 {ch}번 모터 구동]")

        # 90도 이동
        print("-> 90도로 이동")
        kit.servo[ch].angle = 90
        time.sleep(1.5)

        # 180도 이동
        print("-> 180도로 이동")
        kit.servo[ch].angle = 180
        time.sleep(1.5)

        # 안전하게 원래 위치(0도)로 복귀
        print("-> 다시 0도로 원점 복귀")
        kit.servo[ch].angle = 0
        time.sleep(1.5)

if __name__ == "__main__":
    try:
        init_servos()
        test_sequence()
        print("\n=== 모든 모터 테스트가 성공적으로 완료되었습니다! ===")
    except KeyboardInterrupt:
        print("\n사용자에 의해 테스트가 중단되었습니다. 모터를 원점 복귀합니다.")
        for ch in servo_channels:
            try:
                kit.servo[ch].angle = 0
            except:
                pass
