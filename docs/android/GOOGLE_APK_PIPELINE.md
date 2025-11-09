# Google APK Pipeline Integration

Complete guide for building, deploying, and distributing Sentient Core v4 as Android APK applications through Google's pipeline.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [APK Build Pipeline](#apk-build-pipeline)
- [Google Play Integration](#google-play-integration)
- [CI/CD Automation](#cicd-automation)
- [Testing and Validation](#testing-and-validation)
- [Deployment Strategies](#deployment-strategies)
- [Troubleshooting](#troubleshooting)

## Overview

The Google APK Pipeline enables:
- **Android App Development**: Build native Android applications
- **TensorFlow Lite Integration**: On-device AI inference
- **Google Play Distribution**: Automated publishing
- **CI/CD Pipeline**: Automated build and deployment
- **App Bundle Support**: Optimized APK delivery
- **Firebase Integration**: Analytics, ML Kit, and more

### Architecture

```
┌─────────────────────────────────────────────────────┐
│         Sentient Core Android App                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │  UI Layer    │  │  ML Models   │                │
│  │  (Jetpack)   │  │  (TFLite)    │                │
│  └──────────────┘  └──────────────┘                │
│         │                  │                         │
│  ┌──────────────────────────────┐                  │
│  │   Sentient Core Engine       │                  │
│  │   - Reasoning                │                  │
│  │   - Memory                   │                  │
│  │   - Learning                 │                  │
│  └──────────────────────────────┘                  │
│         │                                            │
│  ┌──────────────────────────────┐                  │
│  │   Android Platform Services  │                  │
│  │   - Firebase ML Kit          │                  │
│  │   - Google Play Services     │                  │
│  └──────────────────────────────┘                  │
└─────────────────────────────────────────────────────┘
```

## Prerequisites

### Development Environment

- **Android Studio**: Arctic Fox or later
- **Java Development Kit**: JDK 11 or higher
- **Android SDK**: API Level 24+ (Android 7.0+)
- **Gradle**: 7.0+
- **Python**: 3.9+ (for build scripts)

### Google Services

- **Google Cloud Project**: For APIs and services
- **Firebase Project**: For ML Kit and analytics
- **Google Play Console Account**: For app distribution
- **Service Account**: For API access

### Hardware

- **Development Machine**:
  - 16GB+ RAM
  - 50GB+ free storage
  - Modern multi-core CPU

- **Test Devices**:
  - Android 7.0+ devices
  - Various screen sizes
  - Optional: Devices with Neural Network API support

## Environment Setup

### Step 1: Install Android Studio

```bash
# Download Android Studio
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2023.1.1.28/android-studio-2023.1.1.28-linux.tar.gz

# Extract
tar -xzf android-studio-*.tar.gz -C ~/

# Launch
~/android-studio/bin/studio.sh
```

### Step 2: Configure Android SDK

```bash
# Set environment variables
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Add to ~/.bashrc or ~/.zshrc
echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc

# Install SDK components
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"
```

### Step 3: Setup Google Cloud Project

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Create project
gcloud projects create sentient-core-android --name="Sentient Core Android"

# Set project
gcloud config set project sentient-core-android

# Enable APIs
gcloud services enable androidpublisher.googleapis.com
gcloud services enable firebaseml.googleapis.com
gcloud services enable playintegrity.googleapis.com
```

### Step 4: Setup Firebase

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize Firebase in project
cd ~/sentient-core-v4/android
firebase init

# Select:
# - Firebase ML
# - Analytics
# - Cloud Functions (optional)
```

## APK Build Pipeline

### Project Structure

```bash
# Create Android project structure
cd ~/sentient-core-v4
mkdir -p android/app/src/main/{java,res,assets}
mkdir -p android/app/src/main/ml
```

### Step 1: Configure build.gradle

```groovy
// android/app/build.gradle
plugins {
    id 'com.android.application'
    id 'kotlin-android'
    id 'com.google.gms.google-services'
    id 'com.google.firebase.firebase-perf'
}

android {
    namespace 'ai.sentientcore.android'
    compileSdk 33

    defaultConfig {
        applicationId "ai.sentientcore.android"
        minSdk 24
        targetSdk 33
        versionCode 1
        versionName "4.0.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"

        // ML Model configuration
        aaptOptions {
            noCompress "tflite"
            noCompress "lite"
        }
    }

    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'

            // Code signing
            signingConfig signingConfigs.release
        }
        debug {
            applicationIdSuffix ".debug"
            debuggable true
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_11
        targetCompatibility JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = '11'
    }

    buildFeatures {
        viewBinding true
        mlModelBinding true
        compose true
    }

    composeOptions {
        kotlinCompilerExtensionVersion '1.4.3'
    }
}

dependencies {
    // Core Android
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'

    // Jetpack Compose
    implementation platform('androidx.compose:compose-bom:2023.10.01')
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.material3:material3'
    implementation 'androidx.compose.ui:ui-tooling-preview'
    implementation 'androidx.activity:activity-compose:1.8.2'

    // TensorFlow Lite
    implementation 'org.tensorflow:tensorflow-lite:2.14.0'
    implementation 'org.tensorflow:tensorflow-lite-gpu:2.14.0'
    implementation 'org.tensorflow:tensorflow-lite-support:0.4.4'
    implementation 'org.tensorflow:tensorflow-lite-metadata:0.4.4'
    implementation 'org.tensorflow:tensorflow-lite-task-vision:0.4.4'
    implementation 'org.tensorflow:tensorflow-lite-task-text:0.4.4'

    // Firebase
    implementation platform('com.google.firebase:firebase-bom:32.7.0')
    implementation 'com.google.firebase:firebase-analytics'
    implementation 'com.google.firebase:firebase-ml-modeldownloader'
    implementation 'com.google.firebase:firebase-performance'
    implementation 'com.google.firebase:firebase-crashlytics'

    // Google ML Kit
    implementation 'com.google.mlkit:text-recognition:16.0.0'
    implementation 'com.google.mlkit:image-labeling:17.0.7'
    implementation 'com.google.mlkit:object-detection:17.0.1'

    // Google Play Services
    implementation 'com.google.android.gms:play-services-base:18.3.0'
    implementation 'com.google.android.gms:play-services-mlkit-text-recognition:19.0.0'

    // Networking
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.12.0'

    // Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-play-services:1.7.3'

    // Lifecycle
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.7.0'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'

    // Camera
    implementation 'androidx.camera:camera-camera2:1.3.1'
    implementation 'androidx.camera:camera-lifecycle:1.3.1'
    implementation 'androidx.camera:camera-view:1.3.1'

    // Testing
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}
```

### Step 2: Android Manifest

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
        android:maxSdkVersion="28" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"
        android:maxSdkVersion="32" />

    <!-- Neural Network API support -->
    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.software.nnapi" android:required="false" />

    <application
        android:name=".SentientCoreApp"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.SentientCore"
        android:usesCleartextTraffic="false"
        tools:targetApi="31">

        <!-- Main Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize"
            android:theme="@style/Theme.SentientCore">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Firebase ML Model Download Service -->
        <service
            android:name="com.google.firebase.ml.modeldownloader.FirebaseModelDownloaderService"
            android:exported="false" />

        <!-- Metadata -->
        <meta-data
            android:name="com.google.firebase.ml.modeldownloader.FIREBASE_ML_MODEL_NAMES"
            android:value="sentient-core-model" />

        <meta-data
            android:name="com.google.mlkit.vision.DEPENDENCIES"
            android:value="ocr,label" />

    </application>

</manifest>
```

### Step 3: Build Configuration

```kotlin
// android/build.gradle.kts
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:8.2.0")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.0")
        classpath("com.google.gms:google-services:4.4.0")
        classpath("com.google.firebase:firebase-crashlytics-gradle:2.9.9")
        classpath("com.google.firebase:perf-plugin:1.4.2")
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
```

### Step 4: Build Scripts

```bash
# scripts/build-android.sh
#!/bin/bash

set -e

echo "Building Sentient Core Android APK..."

# Set Android environment
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Navigate to Android project
cd android

# Clean previous builds
./gradlew clean

# Run tests
./gradlew test

# Build debug APK
./gradlew assembleDebug

# Build release APK (requires signing)
./gradlew assembleRelease

# Build App Bundle (for Google Play)
./gradlew bundleRelease

echo "Build complete!"
echo "Debug APK: app/build/outputs/apk/debug/app-debug.apk"
echo "Release APK: app/build/outputs/apk/release/app-release.apk"
echo "App Bundle: app/build/outputs/bundle/release/app-release.aab"
```

## Google Play Integration

### Step 1: App Signing

```bash
# Generate upload key
keytool -genkey -v \
    -keystore ~/sentient-core-upload-key.jks \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -alias sentient-core-upload

# Configure signing in gradle
```

```groovy
// android/app/build.gradle
android {
    signingConfigs {
        release {
            storeFile file(System.getenv("SENTIENT_KEYSTORE_FILE"))
            storePassword System.getenv("SENTIENT_KEYSTORE_PASSWORD")
            keyAlias System.getenv("SENTIENT_KEY_ALIAS")
            keyPassword System.getenv("SENTIENT_KEY_PASSWORD")
        }
    }
}
```

### Step 2: Google Play Console Setup

```bash
# Create service account for API access
gcloud iam service-accounts create sentient-play-publisher \
    --display-name="Sentient Core Play Publisher"

# Grant permissions
gcloud projects add-iam-policy-binding sentient-core-android \
    --member="serviceAccount:sentient-play-publisher@sentient-core-android.iam.gserviceaccount.com" \
    --role="roles/androidpublisher.admin"

# Create and download key
gcloud iam service-accounts keys create ~/sentient-play-publisher-key.json \
    --iam-account=sentient-play-publisher@sentient-core-android.iam.gserviceaccount.com
```

### Step 3: Automated Upload

```python
# scripts/upload-to-play.py
#!/usr/bin/env python3

from googleapiclient.discovery import build
from google.oauth2 import service_account
import argparse

def upload_to_play(package_name, aab_file, track='internal'):
    """Upload APK/AAB to Google Play"""

    # Authenticate
    credentials = service_account.Credentials.from_service_account_file(
        'sentient-play-publisher-key.json',
        scopes=['https://www.googleapis.com/auth/androidpublisher']
    )

    # Build service
    service = build('androidpublisher', 'v3', credentials=credentials)

    # Create edit
    edit_request = service.edits().insert(
        body={},
        packageName=package_name
    )
    result = edit_request.execute()
    edit_id = result['id']

    # Upload AAB
    aab_response = service.edits().bundles().upload(
        editId=edit_id,
        packageName=package_name,
        media_body=aab_file
    ).execute()

    version_code = aab_response['versionCode']

    # Assign to track
    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=track,
        packageName=package_name,
        body={
            'releases': [{
                'versionCodes': [version_code],
                'status': 'completed',
            }]
        }
    ).execute()

    # Commit changes
    commit_request = service.edits().commit(
        editId=edit_id,
        packageName=package_name
    ).execute()

    print(f'Edit "{commit_request["id"]}" has been committed')
    print(f'Version {version_code} deployed to {track}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', required=True)
    parser.add_argument('--aab', required=True)
    parser.add_argument('--track', default='internal')

    args = parser.parse_args()
    upload_to_play(args.package, args.aab, args.track)
```

## CI/CD Automation

### GitHub Actions Workflow

```yaml
# .github/workflows/android-build.yml
name: Android APK Build Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up JDK 11
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'

    - name: Setup Android SDK
      uses: android-actions/setup-android@v2

    - name: Cache Gradle
      uses: actions/cache@v3
      with:
        path: |
          ~/.gradle/caches
          ~/.gradle/wrapper
        key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

    - name: Grant execute permission for gradlew
      run: chmod +x android/gradlew

    - name: Run tests
      run: |
        cd android
        ./gradlew test

    - name: Build debug APK
      run: |
        cd android
        ./gradlew assembleDebug

    - name: Build release AAB
      if: github.event_name == 'release'
      env:
        SENTIENT_KEYSTORE_FILE: ${{ secrets.KEYSTORE_FILE }}
        SENTIENT_KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
        SENTIENT_KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
        SENTIENT_KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
      run: |
        cd android
        echo "${{ secrets.KEYSTORE_FILE_BASE64 }}" | base64 -d > keystore.jks
        ./gradlew bundleRelease

    - name: Upload to Google Play
      if: github.event_name == 'release'
      env:
        PLAY_SERVICE_ACCOUNT_JSON: ${{ secrets.PLAY_SERVICE_ACCOUNT_JSON }}
      run: |
        echo "$PLAY_SERVICE_ACCOUNT_JSON" > service-account.json
        python scripts/upload-to-play.py \
          --package ai.sentientcore.android \
          --aab android/app/build/outputs/bundle/release/app-release.aab \
          --track production

    - name: Upload APK artifact
      uses: actions/upload-artifact@v3
      with:
        name: app-debug
        path: android/app/build/outputs/apk/debug/app-debug.apk
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  ANDROID_COMPILE_SDK: "33"
  ANDROID_BUILD_TOOLS: "33.0.0"
  ANDROID_SDK_TOOLS: "9477386"

before_script:
  - apt-get --quiet update --yes
  - apt-get --quiet install --yes wget tar unzip lib32stdc++6 lib32z1

test:
  stage: test
  script:
    - cd android
    - ./gradlew test
  only:
    - merge_requests
    - develop
    - main

build_debug:
  stage: build
  script:
    - cd android
    - ./gradlew assembleDebug
  artifacts:
    paths:
      - android/app/build/outputs/apk/debug/app-debug.apk
  only:
    - develop
    - main

build_release:
  stage: build
  script:
    - cd android
    - echo "$KEYSTORE_FILE" | base64 -d > keystore.jks
    - ./gradlew bundleRelease
  artifacts:
    paths:
      - android/app/build/outputs/bundle/release/app-release.aab
  only:
    - tags

deploy_play_store:
  stage: deploy
  script:
    - echo "$PLAY_SERVICE_ACCOUNT_JSON" > service-account.json
    - python scripts/upload-to-play.py \
        --package ai.sentientcore.android \
        --aab android/app/build/outputs/bundle/release/app-release.aab \
        --track production
  only:
    - tags
```

## Testing and Validation

### Unit Tests

```kotlin
// android/app/src/test/java/ai/sentientcore/ModelTest.kt
import org.junit.Test
import org.junit.Assert.*

class ModelTest {
    @Test
    fun testModelLoading() {
        val model = SentientCoreModel(context)
        assertNotNull(model)
        assertTrue(model.isLoaded())
    }

    @Test
    fun testInference() {
        val model = SentientCoreModel(context)
        val input = createTestInput()
        val output = model.inference(input)

        assertNotNull(output)
        assertTrue(output.confidence > 0.5)
    }
}
```

### Instrumented Tests

```kotlin
// android/app/src/androidTest/java/ai/sentientcore/UITest.kt
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class UITest {
    @Test
    fun useAppContext() {
        val appContext = InstrumentationRegistry.getInstrumentation().targetContext
        assertEquals("ai.sentientcore.android", appContext.packageName)
    }
}
```

### Firebase Test Lab

```bash
# Upload to Test Lab
gcloud firebase test android run \
  --type instrumentation \
  --app android/app/build/outputs/apk/debug/app-debug.apk \
  --test android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk \
  --device model=Pixel2,version=28,locale=en,orientation=portrait \
  --device model=Pixel3,version=29,locale=en,orientation=portrait
```

## Deployment Strategies

### Internal Testing

```bash
# Deploy to internal testing track
python scripts/upload-to-play.py \
  --package ai.sentientcore.android \
  --aab app-release.aab \
  --track internal
```

### Alpha/Beta Testing

```bash
# Deploy to alpha
python scripts/upload-to-play.py \
  --package ai.sentientcore.android \
  --aab app-release.aab \
  --track alpha

# Deploy to beta
python scripts/upload-to-play.py \
  --package ai.sentientcore.android \
  --aab app-release.aab \
  --track beta
```

### Production Release

```bash
# Staged rollout (10% of users)
python scripts/upload-to-play.py \
  --package ai.sentientcore.android \
  --aab app-release.aab \
  --track production \
  --rollout-percentage 0.1
```

## Troubleshooting

### Build Failures

```bash
# Clean build
cd android
./gradlew clean
rm -rf .gradle

# Rebuild
./gradlew assembleDebug --stacktrace
```

### Signing Issues

```bash
# Verify keystore
keytool -list -v -keystore sentient-core-upload-key.jks

# Check signing config
./gradlew signingReport
```

### API Upload Errors

```bash
# Validate AAB
bundletool validate --bundle=app-release.aab

# Test locally
bundletool build-apks --bundle=app-release.aab --output=app.apks
bundletool install-apks --apks=app.apks
```

## Best Practices

1. **Use App Bundles**: Smaller download sizes
2. **Enable ProGuard**: Code optimization and obfuscation
3. **Test on Multiple Devices**: Use Firebase Test Lab
4. **Monitor Performance**: Firebase Performance Monitoring
5. **Track Crashes**: Firebase Crashlytics
6. **Staged Rollouts**: Gradual production releases
7. **Version Control**: Semantic versioning
8. **Automated Testing**: CI/CD pipeline

## Resources

- [Android Developer Docs](https://developer.android.com/)
- [Google Play Console](https://play.google.com/console)
- [Firebase Console](https://console.firebase.google.com/)
- [TensorFlow Lite](https://www.tensorflow.org/lite/android)

## Next Steps

- [Coral Edge Integration](../coral/CORAL_TRAINING.md)
- [Mobile Deployment Guide](../guides/MOBILE_DEPLOYMENT.md)
- [Performance Optimization](../guides/MOBILE_OPTIMIZATION.md)

---

**Version**: 4.0.0
**Last Updated**: November 2025
**Maintained by**: Sentient Core Team
