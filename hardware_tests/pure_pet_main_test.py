import cv2
import numpy as np
from gpiozero import Button, LED, DistanceSensor, DigitalInputDevice
from time import sleep
from picamera2 import Picamera2
import I2C_LCD_driver

# [1] 하드웨어 핀 설정 및 초기화
button = Button(10)
led = LED(26)
ultrasonic = DistanceSensor(echo=24, trigger=23)
ir_sensors = [
    DigitalInputDevice(17), # 적외선 1
    DigitalInputDevice(27), # 적외선 2
    DigitalInputDevice(22)  # 적외선 3
]

# LCD 초기화
lcd = I2C_LCD_driver.lcd()

# [2] Picamera2 설정 (라즈베리 파이 5 전용)
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

def run_pure_pet():
    print("=== Pure-PET 시스템 가동 중 ===")

    while True:
        # 초기 대기 상태
        lcd.lcd_clear()
        lcd.lcd_display_string("Press Power Btn", 1)
        lcd.lcd_display_string("Ready to Work", 2)
        print("\n[대기] 버튼 입력을 기다립니다...")

        # 버튼이 눌릴 때까지 대기
        button.wait_for_press()

        # [단계 1] 물체 감지 대기 (3초)
        lcd.lcd_clear()
        lcd.lcd_display_string("Searching...", 1)
        print("버튼 클릭! 3초간 물체를 탐색합니다.")

        detected = False
        for _ in range(30): # 0.1초 * 30 = 3초
            if ultrasonic.distance < 0.2: # 20cm 이내 감지
                detected = True
                break
            sleep(0.1)

        if detected:
            # [단계 2] 물체 감지 성공 - 분류 시작
            print(">>> 물체 감지 성공! 분류 시퀀스 시작")
            lcd.lcd_clear()
            lcd.lcd_display_string("Classifying...", 1)

            led.on() # 과정 시작 시 LED 점등

            # [단계 3] 카메라 미리보기 (약 15초 유지)
            # range(150)은 대략 15초 내외입니다.
            for i in range(150):
                frame = picam2.capture_array()
                cv2.imshow('Pure-PET Real-time View', frame)

                # 'q' 키를 누르면 중간에 창 닫기 가능
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # [단계 4] 적외선 데이터 수집 및 가상 분류 작업
            ir_data = [not ir.value for ir in ir_sensors]
            print(f"적외선 데이터 수집 완료: {ir_data}")

            # 실제 분류가 일어나는 것처럼 1초 더 대기
            sleep(1)

            # [단계 5] 종료 및 정리
            led.off() # 모든 과정이 끝나면 LED 소등
            cv2.destroyAllWindows()
            print("분류 프로세스 종료.")

        else:
            # 3초 동안 물체를 못 찾았을 때
            print("물체를 찾지 못했습니다.")
            lcd.lcd_clear()
            lcd.lcd_display_string("No Object Found", 1)
            sleep(2)

try:
    run_pure_pet()
except KeyboardInterrupt:
    print("\n사용자에 의해 시스템이 종료되었습니다.")
finally:
    # 종료 시 하드웨어 안전 정리
    led.off()
    lcd.lcd_clear()
    picam2.stop()
    cv2.destroyAllWindows()
