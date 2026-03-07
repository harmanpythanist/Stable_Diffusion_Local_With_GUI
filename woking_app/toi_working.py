import sys
import torch
from diffusers import StableDiffusionPipeline
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QTextEdit, QFileDialog, QComboBox, QSlider, QScrollArea,
    QFrame
)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal


# Loadingg model from my local computer
print("Loading Stable Diffusion model...")

# Get base directory (works for both .py and .exe)
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(base_dir, "models", "sd_v1_5_local")

pipe = StableDiffusionPipeline.from_pretrained(
    model_path,
    torch_dtype=torch.float32,
    local_files_only=True
).to("cuda")

pipe.safety_checker = None

print("Model loaded!")


# Worker Thread for image-generation
# =========================
class ImageGeneratorThread(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, prompt, steps, num_images, style_text):
        super().__init__()
        self.prompt = prompt
        self.steps = steps
        self.num_images = num_images
        self.style_text = style_text

    def run(self):
        try:
            final_prompt = self.prompt
            if self.style_text:
                final_prompt += ", " + self.style_text

            images = pipe(
                final_prompt,
                num_inference_steps=self.steps,
                height=768,
                width=768,
                num_images_per_prompt=self.num_images
            ).images

            self.finished.emit(images)

        except Exception as e:
            self.error.emit(str(e))



# Main App
# =========================
class AIImageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Image Generator")
        self.setGeometry(150, 50, 1100, 900)

        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #E0E0E0; font-family: Segoe UI; }
            QLabel { color: #E0E0E0; font-size: 13px; }
            QComboBox { background-color: #1e1e1e; color: white; border: 1px solid #555; border-radius: 8px; padding: 5px; }
            QComboBox QAbstractItemView { background-color: #1e1e1e; color: white; selection-background-color: #4CAF50; }
            QSlider::groove:horizontal { background: #444; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #4CAF50; width: 14px; margin: -4px 0; border-radius: 7px; }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 12px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3e8e41; }
            QPushButton:disabled { background-color: gray; }
        """)

        self.generated_images = []
        self.selected_image_index = 0

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # -------------------------
        # Prompt Box
        # -------------------------
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        self.prompt_input.setFont(QFont("Segoe UI", 14))
        self.prompt_input.setMinimumHeight(130)
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                padding: 15px;
                border-radius: 12px;
                border: 2px solid #555;
                background-color: #1e1e1e;
                color: white;
            }
        """)
        main_layout.addWidget(self.prompt_input)

        # -------------------------
        # Controls
        # -------------------------
        settings_frame = QFrame()
        settings_frame.setStyleSheet("QFrame { background-color: #1e1e1e; border-radius: 15px; padding: 20px; }")
        controls_layout = QGridLayout()
        controls_layout.setSpacing(20)

        # Steps
        steps_label = QLabel("Steps")
        steps_label.setStyleSheet("font-weight: 600; font-size: 20px;")
        self.steps_slider = QSlider(Qt.Horizontal)
        self.steps_slider.setMinimum(10)
        self.steps_slider.setMaximum(50)
        self.steps_slider.setValue(25)
        self.steps_value = QLabel("25")
        self.steps_value.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.steps_slider.valueChanged.connect(lambda v: self.steps_value.setText(str(v)))

        steps_layout = QHBoxLayout()
        steps_layout.addWidget(self.steps_slider)
        steps_layout.addWidget(self.steps_value)

        controls_layout.addWidget(steps_label, 0, 0)
        controls_layout.addLayout(steps_layout, 0, 1)

        # Style
        style_label = QLabel("Style Preset")
        style_label.setStyleSheet("font-weight: 600; font-size: 20px;")
        self.style_dropdown = QComboBox()
        self.style_dropdown.addItems(["None", "Realistic", "Anime", "Cyberpunk", "Cinematic"])

        controls_layout.addWidget(style_label, 1, 0)
        controls_layout.addWidget(self.style_dropdown, 1, 1)
        
        # Num of images
        images_label = QLabel("Images to Generate")
        images_label.setStyleSheet("font-weight: 600; font-size: 20px;")
        self.num_images_dropdown = QComboBox()
        self.num_images_dropdown.addItems(["1", "2"])

        controls_layout.addWidget(images_label, 2, 0)
        controls_layout.addWidget(self.num_images_dropdown, 2, 1)

        settings_frame.setLayout(controls_layout)
        main_layout.addWidget(settings_frame)

        # Buttons
        # -------------------------
        btn_layout = QHBoxLayout()

        self.generate_button = QPushButton("Generate Image(s)")
        self.download_button = QPushButton("Download Image")
        self.download_button.setEnabled(False)

        self.generate_button.clicked.connect(self.start_generation)
        self.download_button.clicked.connect(self.download_image)

        btn_layout.addWidget(self.generate_button)
        btn_layout.addWidget(self.download_button)

        main_layout.addLayout(btn_layout)

       
        #  Gallery
        # -------------------------
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout()
        self.scroll_layout.setSpacing(20)
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)

    # Start Generation
    # -------------------------
    def start_generation(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        steps = self.steps_slider.value()
        num_images = int(self.num_images_dropdown.currentText())
        style = self.style_dropdown.currentText()

        style_texts = {
            "None": "",
            "Realistic": "photorealistic, high detail, 8k",
            "Anime": "anime style, vibrant colors, sharp outlines",
            "Cyberpunk": "cyberpunk, neon lights, futuristic city",
            "Cinematic": "cinematic lighting, film grain, epic composition"
        }

        style_text = style_texts.get(style, "")

        self.generate_button.setText("Generating...")
        self.generate_button.setEnabled(False)
        self.download_button.setEnabled(False)

        # Clear previous images
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)

        self.thread = ImageGeneratorThread(prompt, steps, num_images, style_text)
        self.thread.finished.connect(self.display_images)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    # Display Images
    # -------------------------
    def display_images(self, images):
        self.generated_images = images
        self.selected_image_index = 0

        self.generate_button.setText("Generate Image(s)")
        self.generate_button.setEnabled(True)
        self.download_button.setEnabled(True)

        for idx, img in enumerate(images):
            pixmap = self.pil2pixmap(img)
            lbl = QLabel()
            lbl.setPixmap(
                pixmap.scaled(450, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            lbl.setFrameStyle(QFrame.Panel | QFrame.Raised)
            lbl.mousePressEvent = lambda e, i=idx: self.select_image(i)

            self.scroll_layout.addWidget(lbl, 0, idx)

    # -------------------------
    # Select image
    # -------------------------
    def select_image(self, index):
        self.selected_image_index = index


    # Convert PIL to QPixmap
    # -------------------------
    def pil2pixmap(self, image):
        data = image.tobytes("raw", "RGB")
        qimg = QImage(data, image.width, image.height,
                      3 * image.width, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)


    # Download image
    # -------------------------
    def download_image(self):
        if not self.generated_images:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG Files (*.png)"
        )

        if file_path:
            self.generated_images[self.selected_image_index].save(file_path)


    # Error Handling
    # -------------------------
    def show_error(self, message):
        self.generate_button.setText("Generate Image(s)")
        self.generate_button.setEnabled(True)
        print("Error:", message)



# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIImageApp()
    window.show()
    sys.exit(app.exec_())