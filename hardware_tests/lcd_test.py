from RPLCD.i2c import CharLCD
import time

# I2C 주소가 0x27인 경우 (i2cdetect 결과에 따라 0x3f로 바뀔 수 있음)
# 라즈베리 파이 5는 'PCF8574' 드라이버를 주로 사용합니다.
lcd = CharLCD('PCF8574', 0x27)

print("LCD 테스트를 시작합니다.")

try:
    # 화면 초기화
    lcd.clear()

    # 첫 번째 줄 출력
    lcd.write_string("Pure-PET Project")
    lcd.cursor_pos = (1, 0) # 두 번째 줄로 이동

    # 두 번째 줄 출력
    lcd.write_string("System Ready!")

    time.sleep(3)

    while True:
        lcd.clear()
        lcd.write_string("Status: Running")
        time.sleep(1)
        lcd.clear()
        lcd.write_string("Status: Waiting")
        time.sleep(1)

except KeyboardInterrupt:
    lcd.clear()
    lcd.write_string("Test Stopped")
    print("\n테스트 종료")
