# ♻️ Pure-PET (Smart PET Bottle Sorter)
**라즈베리 파이 5 기반 인공지능 페트병 자동 분류 시스템**

## 📌 프로젝트 개요
- **목적**: 페트병의 색상 및 라벨 유무를 판단하여 자동으로 분류하는 스마트 리사이클링 시스템
- **주요 기능**: OpenCV 기반 실시간 영상 처리, 모터 제어를 통한 분류기 구동

## 🛠 하드웨어 구성
- **Main Board**: Raspberry Pi 5 (8GB)
- **Camera**: Raspberry Pi Camera Module 3 (IMX708)
- **Display**: VNC Viewer를 통한 GUI 모니터링

## ⚙️ 개발 환경 및 설정 (중요)
라즈베리 파이 5의 최신 아키텍처(`libcamera`) 대응을 위한 설정입니다.

1. **OS 환경**: Raspberry Pi OS (64-bit) / X11 Window System
2. **가상환경 설정**: 시스템 패키지(OpenCV 등)를 포함하여 생성
   ```bash
   python -m venv --system-site-packages venv
   source venv/bin/activate

## 🛠 Hardware Test Scripts

이 프로젝트는 다양한 센서와 액추에이터를 사용하며, 각 부품의 정상 작동을 확인하기 위한 개별 테스트 코드는 `hardware_tests/` 폴더에 관리합니다.

### 폴더 구조 및 파일 설명
- **hardware_tests/**
  - `camera_test.py`: Raspberry Pi Camera Module 3 및 OpenCV 출력 테스트
  - `led_test.py`: GPIO 26번 기반 고휘도 LED 점등 테스트
  - `ultrasonic_test.py`: HC-SR04 센서를 이용한 거리 측정 및 전압 분배 회로 확인
  - `triple_servo_test.py`: PCA9685 PWM 드라이버를 이용한 3개 서보 모터(5V 5A 외부 전원) 제어 [아직 테스트 못함]
  - `lcd_test.py`: I2C 1602 LCD 화면 출력 및 명암 조절 확인
  - `button_test.py`: GPIO 10번 푸시 버튼 입력 및 내부 풀업 저항 테스트
  - `toggle_test.py`: 버튼 입력에 따른 LED 상태 토글(ON/OFF) 로직 구현
  - `ir_triple_test.py`: 적외선 반사 센서 3개를 이용한 물체 감지 및 투과율 테스트.
      - GPIO 핀: 17(Left), 27(Center), 22(Right)
      - 특징: Active Low(물체 감지 시 0) 특성을 소프트웨어적으로 보정하여 감지 시 'O', 미감지 시 '.'으로 실시간 출력.
      - 가변저항 조절을 통해 투명 페트병과 유색 페트병의 투과율 차이를 판별하는 데 사용.

### 테스트 실행 방법
모든 테스트는 가상환경(`venv`)이 활성화된 상태에서 실행해야 합니다.

```bash
cd ~/pure-pet/hardware_tests
python <파일명>.py
    ex) python hardware_tests/camera_test.py

## 🔌 Hardware Connection Map (Pinout)

모든 제어는 Raspberry Pi 5의 BCM(GPIO) 번호를 기준으로 합니다.

### 1. 센서 및 입력 장치 (Sensors & Inputs)
| 부품명 | 핀 기능 | GPIO 번호 | 물리 핀 번호 | 비고 |
|:---:|:---:|:---:|:---:|:---|
| **적외선(IR) L** | Digital Out | **17** | 11 | 투과율 체크 (왼쪽) |
| **적외선(IR) C** | Digital Out | **27** | 13 | 투과율 체크 (중앙) |
| **적외선(IR) R** | Digital Out | **22** | 15 | 투과율 체크 (오른쪽) |
| **초음파 센서** | Trigger | **23** | 16 | 거리 측정 시작 신호 |
| **초음파 센서** | Echo | **24** | 18 | 전압 분배 회로 필수 (5V -> 3.3V) |
| **푸시 버튼** | Input | **10** | 19 | 내부 풀업 저항 사용 |

### 2. 출력 및 액추에이터 (Outputs & Actuators)
| 부품명 | 핀 기능 | GPIO 번호 | 물리 핀 번호 | 비고 |
|:---:|:---:|:---:|:---:|:---|
| **상태 LED** | Anode(+) | **26** | 37 | 330Ω 저항 연결 필수 |
| **I2C 공통** | SDA | **2** | 3 | LCD, PCA9685 공통 사용 |
| **I2C 공통** | SCL | **3** | 5 | LCD, PCA9685 공통 사용 |

### 3. I2C 장치 주소 (I2C Addresses)
- **LCD 1602**: `0x27`
- **PCA9685 (서보 드라이버)**: `0x40`
