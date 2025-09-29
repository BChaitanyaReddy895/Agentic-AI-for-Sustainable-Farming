# Speech Dependencies Installation Guide

## PyAudio Installation Issues

PyAudio can be tricky to install on Windows. Here are several methods to install it:

### Method 1: Using pip (Recommended)
```bash
pip install pyaudio
```

### Method 2: Using pipwin (Windows)
```bash
pip install pipwin
pipwin install pyaudio
```

### Method 3: Using conda
```bash
conda install pyaudio
```

### Method 4: Pre-compiled wheels
```bash
pip install pipwin
pipwin install pyaudio
```

### Method 5: Manual installation
1. Download the appropriate wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Install using: `pip install downloaded_wheel_file.whl`

## Alternative: Use Text-to-Speech Only

If you can't install PyAudio, the application will still work with:
- ✅ Text-to-Speech (Google TTS)
- ✅ All other features
- ❌ Speech-to-Text (microphone input)

## Troubleshooting

### Error: "Could not find PyAudio"
- Try Method 2 (pipwin) first
- Make sure you have Visual C++ Build Tools installed
- Try using conda instead of pip

### Error: "Microsoft Visual C++ 14.0 is required"
- Install Visual Studio Build Tools
- Or use conda which includes pre-compiled binaries

### Still having issues?
The application works perfectly without voice input - you can still use all the farming features!
