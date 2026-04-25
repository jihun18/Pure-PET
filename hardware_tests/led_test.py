from gpiozero import LED
from time import sleep

# GPIO 26번 핀으로 변경되었습니다.
led_module = LED(26)

print("GPIO 26 기반 고휘도 LED 테스트 시작! (종료: Ctrl+C)")

try:
    while True:
        led_module.on()
        print("LED ON (GPIO 26)")
        sleep(1)

        led_module.off()
        print("LED OFF")
        sleep(1)
except KeyboardInterrupt:
    print("\n테스트를 종료합니다.")
