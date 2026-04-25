from gpiozero import DigitalInputDevice
from time import sleep

# 1. 센서 핀 설정 (GPIO 17, 27, 22)
# DigitalInputDevice는 기본적으로 1(High)과 0(Low)을 읽습니다.
ir_left = DigitalInputDevice(17)
ir_center = DigitalInputDevice(27)
ir_right = DigitalInputDevice(22)

print("=" * 45)
print("   Pure-PET 적외선 3채널 투과율 테스트")
print("   - 감지(O): 빛 반사됨 (불투명/라벨 있음)")
print("   - 미감지(.): 빛 통과/분산 (투명/물체 없음)")
print("=" * 45)
print("종료하려면 Ctrl+C를 누르세요.\n")

try:
    while True:
        # [Active Low 논리 수정]
        # 센서는 물체가 있으면 0(False), 없으면 1(True)을 보냅니다.
        # 이를 'not'으로 뒤집어서 물체가 있을 때 True가 되게 만듭니다.

        l_state = not ir_left.value
        c_state = not ir_center.value
        r_state = not ir_right.value

        # 시각적으로 보기 편하게 표시 (O: 감지됨, .: 미감지)
        l_display = "O" if l_state else "."
        c_display = "O" if c_state else "."
        r_display = "O" if r_state else "."

        # 상태 텍스트 (하나라도 감지되면 상태 표시)
        status_text = ""
        if l_state or c_state or r_state:
            status_text = " << 물체 감지! >>"
        else:
            status_text = "    대기 중...    "

        # 터미널 한 줄에 실시간 출력
        print(f"[{l_display}] [{c_display}] [{r_display}]  (L | C | R) {status_text}", end='\r')

        sleep(0.1) # CPU 부하를 줄이기 위한 짧은 휴식

except KeyboardInterrupt:
    print("\n\n테스트를 종료하고 안전하게 빠져나갑니다.")
