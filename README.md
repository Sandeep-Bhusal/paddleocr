# PaddleOCR Brunei

**PaddleOCR Brunei** is a custom Optical Character Recognition (OCR) project built using [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), designed specifically to detect and extract text from Brunei IDs.  

While it has been trained and optimized for Brunei IDs, it can be adapted for use with IDs or documents from other countries and languages with minor modifications.

---

## Features

- Detects and extracts data even from **small text or low-resolution images**.
- Specially tuned for Brunei ID formats.
- Flexible and extensible for other languages/nations.
- Easy to run: all processing is handled via `main.py`.

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Sandeep-Bhusal/PaddleOcr_Brunei.git
   cd PaddleOcr_Brunei
Install the required packages:

bash
Copy code
pip install -r requirements.txt
Usage
Run the main script:

bash
Copy code
python main.py
Add your ID images to the designated folder (or modify main.py to point to your input).

The script will detect and extract the text fields from the ID automatically.

Example Output
After running main.py, you can expect output like:

yaml
Copy code
Name: John Doe
ID Number: B1234567
Date of Birth: 01/01/1990
Address: Bandar Seri Begawan, Brunei
Even small text fields on the ID are detected and extracted accurately.

Notes
Designed for Brunei IDs but can be adapted to other formats and languages by retraining or adjusting the OCR configurations.

Works with small-sized text and low-resolution images.

Built on top of PaddleOCR for robust and fast text detection.

License
This project is open-source. You are free to use and modify it for personal or commercial purposes.

Author
Sandeep Bhusal
sandeepbhusal85@gmail.com

yaml
Copy code
