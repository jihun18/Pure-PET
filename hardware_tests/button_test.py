from gpiozero import Button, LED
from signal import pause

# 핀 설정
led = LED(26)
btn = Button(10)

def toggle_led():
    # .toggle()은 현재 켜져있으면 끄고, 꺼져있으면 켜주는 함수입니다.
    led.toggle()

    # 터미널에도 현재 상태를 출력해줍니다.
    if led.is_lit:
        print("💡 LED ON: 페트병 인식 모드 활성화")
    else:
        print("🌑 LED OFF: 대기 모드")

# 버튼을 누르는 순간(when_pressed)에만 함수를 실행합니다.
# 손을 떼는 동작(when_released)에는 아무것도 설정하지 않습니다.
btn.when_pressed = toggle_led

print("========================================")
print("   Pure-PET 토글 테스트 모드 시작")
print("   (한 번 누르면 ON, 다시 누르면 OFF)")
print("========================================")

pause()
