FROM apache/airflow:2.10.5  

USER root
# Install dependencies
RUN apt-get update && apt-get install -y wget tar

# Download and install OpenJDK 8 for ARM64
RUN wget https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u322-b06/OpenJDK8U-jdk_aarch64_linux_hotspot_8u322b06.tar.gz && \
    mkdir -p /usr/lib/jvm && \
    tar -xvzf OpenJDK8U-jdk_aarch64_linux_hotspot_8u322b06.tar.gz -C /usr/lib/jvm && \
    mv /usr/lib/jvm/jdk8u322-b06 /usr/lib/jvm/java-8-openjdk-arm64 && \
    update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-8-openjdk-arm64/bin/java 100 && \
    update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/java-8-openjdk-arm64/bin/javac 100 && \
    rm -f OpenJDK8U-jdk_aarch64_linux_hotspot_8u322b06.tar.gz

USER airflow

COPY requirements.txt /requirements.txt


RUN pip install --no-cache-dir -r /requirements.txt
