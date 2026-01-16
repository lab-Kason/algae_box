# Flutter Mobile App - Setup and Build Guide

## 📱 Algae Box Mobile App

Beautiful Material Design 3 app for monitoring and controlling your algae cultivation system.

## Features ✨

- 🌱 **Tank Management**: Create tanks with algae species selection and volume input
- 📊 **Live Dashboard**: Real-time pH, temperature, and turbidity monitoring
- 💡 **Smart Recommendations**: Color-coded advice for pH adjustment, harvest timing
- 🔄 **Auto-refresh**: Updates every 10 seconds
- 📱 **Beautiful UI**: Material Design 3 with smooth animations
- ⚡ **Collection Control**: Start harvest directly from app

## Installation

### 1. Install Flutter

**macOS:**
```bash
# Download Flutter
cd ~/Development
git clone https://github.com/flutter/flutter.git -b stable

# Add to PATH (add to ~/.zshrc)
export PATH="$PATH:$HOME/Development/flutter/bin"

# Reload shell
source ~/.zshrc

# Check installation
flutter doctor
```

### 2. Install Android Studio

1. Download: https://developer.android.com/studio
2. Install Android Studio
3. Open → Tools → SDK Manager
4. Install Android SDK (API 33+)
5. Accept licenses:
```bash
flutter doctor --android-licenses
```

### 3. Verify Setup

```bash
flutter doctor -v
```

You should see:
- ✅ Flutter (Channel stable)
- ✅ Android toolchain

## Build & Run

### Option A: Run on Android Phone (Recommended)

1. **Enable Developer Mode on your Android phone:**
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → System → Developer Options → Enable "USB Debugging"

2. **Connect phone via USB**

3. **Check device is detected:**
```bash
cd mobile_app
flutter devices
```

4. **Run the app:**
```bash
flutter run
```

The app will install and run on your phone!

### Option B: Build APK File

Build a release APK you can install on any Android phone:

```bash
cd mobile_app

# Build APK
flutter build apk --release

# APK location:
# build/app/outputs/flutter-apk/app-release.apk
```

**Install APK on phone:**
1. Copy `app-release.apk` to your phone
2. Open file manager → tap APK
3. Allow "Install from unknown sources"
4. Install!

### Option C: Build for Google Play Store

```bash
# Build App Bundle (for Play Store)
flutter build appbundle --release

# Output: build/app/outputs/bundle/release/app-release.aab
```

## Project Structure

```
mobile_app/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── models/
│   │   └── models.dart           # Data models (Tank, Sensor, etc.)
│   ├── services/
│   │   └── api_service.dart      # Railway API integration
│   ├── screens/
│   │   ├── home_screen.dart      # Tank list
│   │   ├── create_tank_screen.dart
│   │   ├── tank_dashboard_screen.dart
│   │   └── recommendations_screen.dart
│   └── widgets/
│       └── (custom widgets if needed)
└── pubspec.yaml                  # Dependencies
```

## Troubleshooting

### "Flutter not found"
```bash
export PATH="$PATH:$HOME/Development/flutter/bin"
source ~/.zshrc
```

### "No devices found"
- Enable USB debugging on phone
- Check USB cable works for data transfer
- Run: `flutter doctor`

### "Gradle build failed"
```bash
cd mobile_app/android
./gradlew clean
cd ..
flutter pub get
flutter run
```

### "API connection failed"
- Check API URL in `lib/services/api_service.dart`
- Make sure it's: `https://web-production-f856a8.up.railway.app`
- Test in browser first

## Configuration

### Change API URL

Edit `mobile_app/lib/services/api_service.dart`:

```dart
static const String baseUrl = 'https://YOUR-URL.railway.app';
```

When Raspberry Pi arrives, change to local IP:
```dart
static const String baseUrl = 'http://192.168.1.XXX:5001';
```

## First Run

1. App opens → Shows "No Tanks Yet"
2. Tap "Create Tank" button
3. Fill form:
   - Tank Name: "My First Tank"
   - Algae Species: Select from dropdown (Chlorella, Spirulina, etc.)
   - Volume: Enter in liters (e.g., 100)
4. Tap "Create Tank"
5. Tank appears on home screen
6. Tap tank → View dashboard

## App Screenshots Description

**Home Screen:**
- List of all tanks with species and volume
- Green cards with tank info
- Floating "New Tank" button

**Tank Dashboard:**
- Tank info card (species + volume displayed)
- pH card (blue) with value and status icon
- Temperature card (orange) with °C
- Turbidity card (teal) with NTU
- "Start Collection" button (orange when harvest ready)
- "View Recommendations" button
- Auto-refreshes every 10 seconds

**Create Tank:**
- Beautiful form with species dropdown
- Shows species details when selected
- Volume input in liters
- Real-time validation

**Recommendations:**
- Color-coded cards (red=critical, orange=action, green=ok)
- Clear issue descriptions
- Specific actions to take
- Target values shown

## Support

For issues, check:
1. Flutter version: `flutter --version`
2. API health: Visit `https://web-production-f856a8.railway.app/api/health`
3. Device logs: `flutter logs`

---

**Made with ❤️ for Algae Box Smart Cultivation System**
