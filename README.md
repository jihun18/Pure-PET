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
