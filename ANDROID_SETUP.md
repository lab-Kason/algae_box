# Android Setup Guide

## Step 1: Install Android Studio (MANUAL - 10 minutes)
1. Go to https://developer.android.com/studio
2. Click "Download Android Studio"
3. Run the installer
4. Follow setup wizard (keep all default options)
5. Wait for SDK components to download

## Step 2: Accept Android Licenses (AUTOMATED)
After Android Studio installs, run:
```bash
flutter doctor --android-licenses
```
Press 'y' for each license.

## Step 3: Build APK (AUTOMATED)
```bash
cd /Users/kasonchiu/Documents/GitHub/algae_box/mobile_app
flutter pub get
flutter build apk --release
```

APK will be at: `mobile_app/build/app/outputs/flutter-apk/app-release.apk`

## Step 4: Install on Phone (MANUAL - 2 minutes)

### Option A: USB Transfer
1. Connect phone via USB
2. Enable "File Transfer" mode on phone
3. Copy app-release.apk to phone's Downloads folder
4. On phone: Settings → Security → Enable "Install unknown apps"
5. Open Downloads, tap app-release.apk, tap "Install"

### Option B: AirDrop (if phone nearby)
1. Open Finder
2. AirDrop the APK to your phone
3. On phone: tap APK notification
4. Settings → Security → Enable "Install unknown apps"
5. Tap "Install"

### Option C: Email
1. Email the APK to yourself
2. Open email on phone
3. Download attachment
4. Follow security steps and install

## Step 5: Test App
1. Open "Algae Monitor" app
2. Create a tank (select species, enter volume)
3. View dashboard with live sensor data
4. Check recommendations

Done! 🎉
