# Flutter Setup for Algae Box Mobile App

## Install Flutter (macOS)

### 1. Download Flutter
```bash
cd ~/Development  # or wherever you want to install
git clone https://github.com/flutter/flutter.git -b stable
```

### 2. Add to PATH
Add to your `~/.zshrc`:
```bash
export PATH="$PATH:$HOME/Development/flutter/bin"
```

Then reload:
```bash
source ~/.zshrc
```

### 3. Run Flutter Doctor
```bash
flutter doctor
```

This will check what you need to install:
- ✅ Flutter SDK
- ❓ Android Studio (needed for Android development)
- ❓ Xcode (needed for iOS, optional for now)

### 4. Install Android Studio
1. Download from: https://developer.android.com/studio
2. Install Android Studio
3. Open Android Studio → Tools → SDK Manager
4. Install Android SDK (API 33 or higher)

### 5. Accept Android Licenses
```bash
flutter doctor --android-licenses
```

### 6. Verify Setup
```bash
flutter doctor -v
```

You should see checkmarks for:
- ✅ Flutter
- ✅ Android toolchain

## Alternative: Quick Test Without Installation

If you want to see the code first before installing Flutter, I can:
1. Create all the Flutter code now
2. You install Flutter later
3. Then build APK when ready

**Your choice:**
- A) Install Flutter now (30 min setup)
- B) I create the code now, you install Flutter later
