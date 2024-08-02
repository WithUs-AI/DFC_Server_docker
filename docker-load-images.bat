@echo off
echo Loading Docker images...

echo Loading dfc_mysql_image...
docker load -i .\dfc_mysql_image.tar
if %errorlevel% neq 0 (
    echo Error loading dfc_mysql_image
    pause
    exit /b %errorlevel%
)

echo Loading hailo_sw_suite_2023-07.1...
docker load -i .\hailo_sw_suite_2023-07.1.tar
if %errorlevel% neq 0 (
    echo Error loading hailo_sw_suite_2023-07.1
    pause
    exit /b %errorlevel%
)

echo All tasks completed successfully.
pause