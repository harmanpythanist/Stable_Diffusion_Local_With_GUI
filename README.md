Generate images in your laptop without internet. 

Download model once by running the code in file **download and use model locally.ipynb**. You will need internet to download the model. 

After download is done, use it by running **TOI_with_gui_working.ipynb**


---

## Working Code File:

- Python version I used: 3.10.10

### Install these in a VENV:

- pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
  
- pip install diffusers transformers accelerate safetensors
  
- pip install pyqt5 pillow
  
- pip install pyinstaller

- pip install requests

### Then:

- pyinstaller --clean --noconfirm --windowed --icon=icon.ico --collect-all torch --collect-all diffusers --collect-all requests toi_working.py

- It will generate app in dist folder.
  
Download the model locally and keep in same folder as your app.

