from gpiozero import DistanceSensor
from time import sleep

# echo=24, trigger=23번 핀 설정
# threshold_distance를 설정해 특정 거리 안에 들어오면 반응하게 할 수도 있습니다.
sensor = DistanceSensor(echo=24, trigger=23)

print("초음파 센서 테스트를 시작합니다. (종료: Ctrl+C)")

try:
    while True:
        # sensor.distance는 0~1 사이의 값(미터 단위)을 반환합니다.
        # 이를 cm로 바꾸기 위해 100을 곱해줍니다.
        distance_cm = sensor.distance * 100

        print(f"현재 거리: {distance_cm:.1f} cm")

        # 거리에 따라 반응 (예: 10cm 이내면 물체 감지)
        if distance_cm < 10:
            print("=> 물체 감지!")

        sleep(0.5) # 0.5초 간격으로 측정

except KeyboardInterrupt:
    print("\n테스트를 종료합니다.")
