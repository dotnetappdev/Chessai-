# Building Distribution Package

## Prerequisites

```bash
pip install -r requirements.txt
```

## Build Steps

### 1. Standard Build (Folder with DLLs)

This creates a folder with the executable and all required DLLs:

```bash
pyinstaller ChessAI.spec
```

**Output**: `dist/ChessAI/` folder containing:
- `ChessAI.exe` (main executable)
- Various DLL files
- Python runtime
- All dependencies

**Size**: ~50-100 MB without TensorFlow

**Pros**: 
- Faster startup
- Easier to debug
- Smaller individual files

**Cons**:
- Multiple files to distribute
- Users see folder structure

### 2. Single-File Build (Optional)

Create a single executable file:

```bash
pyinstaller --onefile --windowed --name ChessAI main.py
```

**Output**: `dist/ChessAI.exe` (single file)

**Size**: ~80-120 MB

**Pros**:
- Single file distribution
- Cleaner appearance

**Cons**:
- Slower startup (extracts to temp)
- Larger single file
- May trigger antivirus warnings

### 3. With TensorFlow (AI Learning)

If you want full AI training capabilities:

```bash
# Install TensorFlow first
pip install tensorflow

# Build normally
pyinstaller ChessAI.spec
```

**Size**: ~400-600 MB (TensorFlow is large)

## Distribution

### Folder Distribution (Recommended)
1. Navigate to `dist/ChessAI/`
2. Zip the entire folder
3. Share the zip file
4. Users extract and run `ChessAI.exe`

### Single File Distribution
1. Find `dist/ChessAI.exe`
2. Share the single file
3. Users download and run directly

## Testing the Build

Before distributing:

```bash
# Test the executable
cd dist/ChessAI
./ChessAI.exe  # Windows
./ChessAI      # Linux/Mac

# Test on clean system without Python installed
```

## Code Signing (Optional)

For Windows distribution without security warnings:

1. Obtain a code signing certificate
2. Sign the executable:

```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/ChessAI/ChessAI.exe
```

## Creating an Installer (Optional)

### Using Inno Setup (Windows)

1. Install Inno Setup: https://jrsoftware.org/isinfo.php
2. Create script:

```iss
[Setup]
AppName=3D Chess AI
AppVersion=1.0
DefaultDirName={pf}\ChessAI
DefaultGroupName=3D Chess AI
OutputDir=installer
OutputBaseFilename=ChessAI-Setup

[Files]
Source: "dist\ChessAI\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\3D Chess AI"; Filename: "{app}\ChessAI.exe"
Name: "{userdesktop}\3D Chess AI"; Filename: "{app}\ChessAI.exe"
```

3. Compile with Inno Setup
4. Get `installer/ChessAI-Setup.exe`

## Troubleshooting Build Issues

### Missing Modules
```bash
# Add to hiddenimports in ChessAI.spec:
hiddenimports=['missing_module_name'],
```

### Import Errors
```bash
# Test imports before building:
python -c "import main"
```

### Size Too Large
```bash
# Exclude unnecessary modules:
excludes=['matplotlib', 'scipy', 'pandas'],
```

### DLL Errors
```bash
# Update PyInstaller:
pip install --upgrade pyinstaller
```

## Optimization

### Reduce Size
1. Remove TensorFlow if AI training not needed
2. Use `--exclude-module` for unused packages
3. Enable UPX compression (already enabled in spec)

### Faster Startup
1. Use folder distribution instead of single file
2. Minimize hidden imports
3. Remove debugging symbols

## Platform-Specific Notes

### Windows
- Builds work on Windows 7+
- No special requirements
- May need VC++ redistributables

### Linux
- May need to install `libGL` and `libGLU`
- Use system package manager: `sudo apt install libgl1-mesa-glx libglu1-mesa`

### macOS
- Creates `.app` bundle automatically
- Code signing recommended for distribution
- May need to notarize for Gatekeeper

## Version Information

Add version info to executable (Windows):

Create `version.txt`:
```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'Your Name'),
        StringStruct('FileDescription', '3D Chess AI'),
        StringStruct('FileVersion', '1.0.0'),
        StringStruct('ProductName', '3D Chess AI'),
        StringStruct('ProductVersion', '1.0.0'),
      ])
    ])
  ]
)
```

Add to spec file:
```python
exe = EXE(
    ...
    version='version.txt',
    ...
)
```

## Final Checklist

Before release:
- [ ] Test on clean Windows system
- [ ] Test all features (play, save, load, AI)
- [ ] Check file size is reasonable
- [ ] Verify no console window appears
- [ ] Test 3D rendering works
- [ ] Include README and license
- [ ] Sign executable (optional)
- [ ] Create installer (optional)
- [ ] Test antivirus scan results
