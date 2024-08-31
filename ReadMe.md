# 도커 환경 설치하기
1. virtualbox 데스크탑 다운로드
2. virtualbox 설치
VirtualBox-7.0.8-156879-Win.exe를 사용합니다.
3. virtualbox 이미지 다운로드
https://drive.google.com/file/d/1u9N7nKwm5K69y76mysF6LPzCgwGcBvmn/view?usp=sharing
4. DFC_SYSTEM 폴더 받기

# 도커 환경 설정하기
1. hailo 홈페이지에서 'hailo_sw_suite_2023-07.1.tar' 설치하기
2. docker-load-images.bat 실행하기
3. 도커 데스크탑을 실행하고 Terminal 버튼을 클릭하여 창 오픈
4. cd 명령어를 이용하여 DFC_SYSTEM 폴더 경로로 이동
5. docker-compose up -d 엔터 - (hailo_sw 환경은 죽고나서 재실행 해줘야합니다.)<br> *이유 mysql 백업 적용이 느림*
