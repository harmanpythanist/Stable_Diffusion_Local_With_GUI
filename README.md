# Offline Image Generator with PyQt5 GUI

Generate images **locally on your laptop without an internet connection** using Stable Diffusion.

The model only needs to be downloaded **once**. After that, image generation works completely **offline**.

---

## 📥 Download the Model (One-time Setup)

Run the notebook:

```
download and use model locally.ipynb
```

⚠️ Internet is required only for this step to download the model.

After the model is downloaded, it will be stored locally and can be reused anytime.

---

## 🚀 Run the Image Generator

Once the model is downloaded, run:

```
TOI_with_gui_working.ipynb
```

This will launch the **GUI-based image generator**.

---

## Development Setup: (Working App)

### Python Version
```
Python 3.10.10
```

### Create a Virtual Environment (Recommended)

```
python -m venv venv
venv\Scripts\activate
```

---

## Required Libraries

Install the following packages inside the virtual environment:

```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install diffusers transformers accelerate safetensors
pip install pyqt5 pillow
pip install pyinstaller
pip install requests
```

---

## Build the Desktop Application

Run the following command to create the executable:

```
pyinstaller --clean --noconfirm --windowed --icon=icon.ico --collect-all torch --collect-all diffusers --collect-all requests toi_working.py
```

After the build finishes, the application will appear in:

```
dist/
```

---

## 📁 Model Placement

Download the model locally and place it in the **same folder as the generated application**.

Example structure:

```
dist/
 └── toi_working/
     ├── toi_working.exe
     ├── models/
     │    └── sd_v1_5_local
```

---

## ✨ Features
 
- Works **without internet after setup**   
- Simple GUI interface  
- Packaged as a desktop application
