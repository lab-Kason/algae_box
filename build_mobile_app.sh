#!/bin/bash
# Quick Build Script for Algae Box Mobile App

echo "🌱 Algae Box - Mobile App Builder"
echo "=================================="
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter not found!"
    echo ""
    echo "Please install Flutter first:"
    echo "1. Visit: https://docs.flutter.dev/get-started/install"
    echo "2. Or run: cd ~/Development && git clone https://github.com/flutter/flutter.git -b stable"
    echo "3. Add to PATH: export PATH=\"\$PATH:\$HOME/Development/flutter/bin\""
    exit 1
fi

echo "✅ Flutter found: $(flutter --version | head -1)"
echo ""

cd mobile_app

# Get dependencies
echo "📦 Installing dependencies..."
flutter pub get

echo ""
echo "What would you like to do?"
echo "1) Run on connected Android phone"
echo "2) Build APK file"
echo "3) Just check if everything is ready"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📱 Running on device..."
        flutter run
        ;;
    2)
        echo ""
        echo "🔨 Building APK..."
        flutter build apk --release
        echo ""
        echo "✅ APK built successfully!"
        echo "📁 Location: mobile_app/build/app/outputs/flutter-apk/app-release.apk"
        echo ""
        echo "To install on your phone:"
        echo "1. Copy app-release.apk to your phone"
        echo "2. Open it and allow installation from unknown sources"
        ;;
    3)
        echo ""
        echo "🔍 Checking setup..."
        flutter doctor -v
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
