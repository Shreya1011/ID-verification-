## Document Verification Service

This is a Flask-based document verification service that extracts and verifies details (like name, date of birth, and identification numbers) from images or PDFs of various government-issued documents such as Aadhaar cards, PAN cards, Voter IDs, and Driving Licenses. The service utilizes Optical Character Recognition (OCR) to extract text from images or PDF files and cross-checks the extracted details against a database of known records.

---

### Features

1. **Document Type Support**: 
   - Aadhaar Card
   - PAN Card
   - Voter ID
   - Driving License

2. **Input Types Supported**:
   - Image files (`jpg`, `jpeg`, `png`)
   - PDF files (only for Driving License, where text is extracted from the PDF pages)

3. **Key Data Extraction**:
   - Name
   - Date of Birth
   - Identification Number (Aadhaar Number, PAN Number, Voter ID Number, or Driving License Number)

4. **Database Verification**:
   - The extracted ID numbers (Aadhaar, PAN, Voter ID, and Driving License) are compared against a MySQL database containing the respective ID records.

5. **OCR for Text Extraction**:
   - Uses Tesseract OCR to extract text from images and PDFs.

---

### Installation

Follow these steps to set up the project:

#### Prerequisites

- Python 3.x
- MySQL Database

#### Dependencies

Install required Python packages by running the following command:

```bash
pip install Flask pytesseract Pillow mysql-connector pdf2image
```

Additionally, ensure you have **Tesseract** OCR installed on your system. You can download it from [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract).

For Linux (Ubuntu), you can install Tesseract using:

```bash
sudo apt install tesseract-ocr
```

For macOS, use Homebrew:

```bash
brew install tesseract
```

#### Database Setup

Set up a MySQL database to store the ID numbers for validation. Example tables:

1. **Aadhar Table**: Stores Aadhaar numbers.
2. **PAN Table**: Stores PAN numbers.
3. **Voter Table**: Stores Voter ID numbers.
4. **Driving License Table**: Stores Driving License numbers.

Ensure that each table has a column to store the respective identification numbers (e.g., `aadhar_number`, `pan_number`, etc.).

---

### Project Structure

```
document-verification-service/
│
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies file
├── templates/
│   └── index.html            # (Optional) Frontend for uploading documents
├── static/                   # Static files (for serving frontend assets)
└── config.py                 # (Optional) Configuration file for database credentials
```

---

### How It Works

The application exposes a `/extract-details` API endpoint which accepts a POST request with the following form data:

- **documenttype**: The type of the document (`aadhar`, `pan`, `voter`, or `dl`).
- **document**: The file to be processed (either an image or a PDF).

#### Endpoint: `/extract-details`

**Request Example**:

```bash
curl -X POST -F "documenttype=aadhar" -F "document=@path_to_image.jpg" http://localhost:5000/extract-details
```

The service will:
1. Extract the text from the uploaded document using Tesseract OCR.
2. Identify the relevant details (name, date of birth, and ID number).
3. Check if the extracted ID number exists in the corresponding database table.
4. Return a JSON response with the extracted details and database verification results.

---

### Functions Breakdown

#### 1. **extract_text_from_image(image_path)**:
   - Extracts text from an image using Tesseract OCR.
   
#### 2. **extract_text_from_pdf(pdf_path)**:
   - Converts PDF pages into images and then uses Tesseract OCR to extract text from each page.

#### 3. **find_12_digit_number_with_spaces(text)**:
   - Searches for and extracts the Aadhaar number in the format `xxxx xxxx xxxx` from the extracted text.

#### 4. **find_pan_number(text)**:
   - Extracts the PAN number in the format `ABCDE1234F` from the text.

#### 5. **find_voter_id_number(text)**:
   - Extracts the Voter ID number, which is typically in the format `XXX1234567`.

#### 6. **find_driving_license_number(text)**:
   - Extracts the Driving License number, which follows the format `XX12 12345678901`.

#### 7. **find_name_and_dob_aadhar(text)**:
   - Extracts the name and date of birth from an Aadhaar card's text.

#### 8. **find_name_and_dob_pan(text)**:
   - Extracts the name and date of birth from a PAN card's text.

#### 9. **find_name_and_dob_voter(text)**:
   - Extracts the name and date of birth from a Voter ID's text.

#### 10. **find_name_and_dob_driving(text)**:
   - Extracts the name and date of birth from a Driving License's text.

#### 11. **fetch_numbers_from_db(table_name, column_name)**:
   - Fetches all the ID numbers from a specific table in the database for comparison.

#### 12. **extract_details()**:
   - The main Flask route that handles the incoming document, extracts details, and returns the response.

---

### Example Response

For a successful request with a valid Aadhaar document, the response will look like this:

```json
{
    "document_type": "Aadhaar",
    "details": {
        "dob": "01/01/1980",
        "name": "John Doe",
        "number": "123412341234",
        "found_in_db": true
    }
}
```

If the document does not contain valid data or is unsupported, the response will contain an error message, like so:

```json
{
    "error": "Unsupported document type"
}
```

---

### Skills & Technologies Used

- **Flask**: Web framework to build the API.
- **Tesseract OCR**: Optical character recognition for extracting text from images and PDFs.
- **Python**: Core programming language.
- **MySQL**: Relational database to store and fetch ID numbers.
- **Pillow (PIL)**: Python Imaging Library to handle image files.
- **pdf2image**: Converts PDF pages to images for OCR processing.

---


### Acknowledgments

- Tesseract OCR for providing an open-source OCR engine.
- Flask for the web framework.
- Pillow and pdf2image for their image and PDF handling utilities.
