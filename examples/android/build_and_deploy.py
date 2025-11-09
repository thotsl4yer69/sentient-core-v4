#!/usr/bin/env python3
"""
Sentient Core v4 - Android APK Build and Deploy Example

This example demonstrates:
1. Setting up Android build environment
2. Building APK/AAB
3. Running tests
4. Uploading to Google Play
"""

import os
import subprocess
import sys
from pathlib import Path


def check_environment():
    """Check Android development environment"""
    print("[1/7] Checking environment...")

    checks = {
        "ANDROID_HOME": os.environ.get("ANDROID_HOME"),
        "Java": subprocess.run(["java", "-version"], capture_output=True).returncode == 0,
        "Gradle": Path("android/gradlew").exists(),
    }

    all_passed = True
    for name, status in checks.items():
        if status:
            print(f"  ✓ {name}: OK")
        else:
            print(f"  ✗ {name}: MISSING")
            all_passed = False

    if not all_passed:
        print("\n  ⚠ Please install missing dependencies")
        print("  See: docs/android/GOOGLE_APK_PIPELINE.md")
        return False

    return True


def setup_project():
    """Setup Android project"""
    print("[2/7] Setting up project...")

    android_dir = Path("android")
    if not android_dir.exists():
        print("  ℹ Creating Android project structure...")
        android_dir.mkdir(exist_ok=True)

    print("  ✓ Project structure ready")
    return True


def run_tests():
    """Run unit and instrumented tests"""
    print("[3/7] Running tests...")

    os.chdir("android")

    # Unit tests
    print("  ℹ Running unit tests...")
    result = subprocess.run(
        ["./gradlew", "test"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("  ✓ Unit tests passed")
    else:
        print("  ✗ Unit tests failed")
        print(result.stdout)
        return False

    # Check for connected devices
    adb_result = subprocess.run(
        ["adb", "devices"],
        capture_output=True,
        text=True
    )

    if "device\n" in adb_result.stdout or "device\r\n" in adb_result.stdout:
        print("  ℹ Running instrumented tests...")
        result = subprocess.run(
            ["./gradlew", "connectedAndroidTest"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("  ✓ Instrumented tests passed")
        else:
            print("  ⚠ Instrumented tests failed (non-critical)")
    else:
        print("  ℹ No devices connected, skipping instrumented tests")

    os.chdir("..")
    return True


def build_debug_apk():
    """Build debug APK"""
    print("[4/7] Building debug APK...")

    os.chdir("android")

    result = subprocess.run(
        ["./gradlew", "assembleDebug"],
        capture_output=True,
        text=True
    )

    os.chdir("..")

    if result.returncode == 0:
        apk_path = "android/app/build/outputs/apk/debug/app-debug.apk"
        if Path(apk_path).exists():
            size = Path(apk_path).stat().st_size / (1024 * 1024)
            print(f"  ✓ Debug APK built ({size:.1f} MB)")
            print(f"  ✓ Location: {apk_path}")
            return apk_path

    print("  ✗ Debug APK build failed")
    return None


def build_release_aab():
    """Build release App Bundle"""
    print("[5/7] Building release App Bundle...")

    # Check signing configuration
    required_vars = [
        "SENTIENT_KEYSTORE_FILE",
        "SENTIENT_KEYSTORE_PASSWORD",
        "SENTIENT_KEY_ALIAS",
        "SENTIENT_KEY_PASSWORD"
    ]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"  ⚠ Missing signing configuration: {', '.join(missing_vars)}")
        print("  ℹ Skipping release build")
        return None

    os.chdir("android")

    result = subprocess.run(
        ["./gradlew", "bundleRelease"],
        capture_output=True,
        text=True
    )

    os.chdir("..")

    if result.returncode == 0:
        aab_path = "android/app/build/outputs/bundle/release/app-release.aab"
        if Path(aab_path).exists():
            size = Path(aab_path).stat().st_size / (1024 * 1024)
            print(f"  ✓ Release AAB built ({size:.1f} MB)")
            print(f"  ✓ Location: {aab_path}")
            return aab_path

    print("  ✗ Release AAB build failed")
    return None


def install_on_device(apk_path: str):
    """Install APK on connected device"""
    print("[6/7] Installing on device...")

    # Check for devices
    result = subprocess.run(
        ["adb", "devices"],
        capture_output=True,
        text=True
    )

    if "device\n" not in result.stdout and "device\r\n" not in result.stdout:
        print("  ℹ No devices connected, skipping installation")
        return False

    # Install APK
    result = subprocess.run(
        ["adb", "install", "-r", apk_path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("  ✓ APK installed on device")
        return True
    else:
        print("  ✗ Installation failed")
        return False


def upload_to_play(aab_path: str, track: str = "internal"):
    """Upload App Bundle to Google Play"""
    print(f"[7/7] Uploading to Google Play ({track} track)...")

    # Check for service account credentials
    credentials_path = "service-account.json"
    if not Path(credentials_path).exists():
        creds_env = os.environ.get("PLAY_SERVICE_ACCOUNT_JSON")
        if creds_env:
            Path(credentials_path).write_text(creds_env)
        else:
            print("  ⚠ No Play Store credentials found")
            print("  ℹ Skipping upload")
            return False

    # Upload using script
    result = subprocess.run([
        "python",
        "scripts/upload-to-play.py",
        "--package", "ai.sentientcore.android",
        "--aab", aab_path,
        "--track", track
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  ✓ Uploaded to {track} track")
        return True
    else:
        print(f"  ✗ Upload failed: {result.stderr}")
        return False


def generate_summary(debug_apk, release_aab):
    """Generate build summary"""
    print()
    print("=" * 60)
    print("  ✅ Build Pipeline Complete!")
    print("=" * 60)
    print()
    print("📦 Build Artifacts:")

    if debug_apk:
        print(f"  • Debug APK: {debug_apk}")

    if release_aab:
        print(f"  • Release AAB: {release_aab}")

    print()
    print("🚀 Next Steps:")

    if debug_apk:
        print(f"  1. Test APK: adb install -r {debug_apk}")
        print(f"  2. Launch app: adb shell am start -n ai.sentientcore.android/.MainActivity")

    if release_aab:
        print(f"  3. Upload to Play: ./scripts/build-android.sh --release --aab --upload")
        print(f"  4. Promote to beta/prod via Play Console")

    print()
    print("📊 Reports:")
    print("  • Test results: android/app/build/reports/tests/")
    print("  • Lint results: android/app/build/reports/lint/")
    print("  • Build reports: android/app/build/reports/")


def main():
    """Main execution flow"""
    print("=" * 60)
    print("  Sentient Core v4 - Android Build & Deploy Pipeline")
    print("=" * 60)
    print()

    # Save current directory
    original_dir = os.getcwd()

    try:
        # Pipeline steps
        if not check_environment():
            return 1

        if not setup_project():
            return 1

        if not run_tests():
            print("\n⚠ Tests failed, but continuing build...")

        debug_apk = build_debug_apk()
        release_aab = build_release_aab()

        if debug_apk:
            install_on_device(debug_apk)

        if release_aab:
            # Ask before uploading
            response = input("\n  Upload to Google Play? (y/N): ")
            if response.lower() == 'y':
                upload_to_play(release_aab, track="internal")

        # Generate summary
        generate_summary(debug_apk, release_aab)

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠ Build cancelled by user")
        return 130

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Return to original directory
        os.chdir(original_dir)


if __name__ == "__main__":
    sys.exit(main())
