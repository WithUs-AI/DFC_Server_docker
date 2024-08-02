FROM khipu/openjdk17-alpine
ARG JAR_FILE=*.jar
COPY ${JAR_FILE} app.jar
LABEL authors="JEONGBYEONGCHAN"

ENTRYPOINT ["java", "-jar","/app.jar"]