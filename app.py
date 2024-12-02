from flask import Flask, jsonify, request
import pytesseract
from PIL import Image
import re
import mysql.connector
from pdf2image import convert_from_path
import os

app = Flask(__name__)

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ''
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

def find_12_digit_number_with_spaces(text):
    match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    return match.group().replace(" ", "") if match else None

def find_pan_number(text):
    match = re.search(r'\b[A-Z]{5}\d{4}[A-Z]\b', text)
    return match.group() if match else None

def find_voter_id_number(text):
    match = re.search(r'\b[A-Z]{3}\d{7}\b', text)
    return match.group() if match else None

def find_driving_license_number(text):
    match = re.search(r'\b[A-Z]{2}\d{2}\s\d{11}\b', text)
    return match.group() if match else None

def find_name_and_dob_aadhar(text):
    dob = re.search(r'\b\d{2}/\d{2}/\d{4}\b', text)
    lines = text.split('\n')
    name = None
    for i, line in enumerate(lines):
        if dob and dob.group() in line:
            if i > 0:
                name = lines[i - 1].strip()
            break
    details = {
        'dob': dob.group() if dob else None,
        'name': name
    }
    return details

def find_name_and_dob_pan(text):
    dob = None
    name = None
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if "Date of Birth" in line:
            if i < len(lines) - 1:
                dob_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', lines[i + 1])
                if dob_match:
                    dob = dob_match.group()
        if "Name" in line:
            if "Father's Name" not in line:
                if i < len(lines) - 1:
                    name = lines[i + 1].strip()
                    if "Father's Name" in name:
                        name = None
            break
    details = {
        'dob': dob,
        'name': name
    }
    return details

def find_name_and_dob_voter(text):
    dob = re.search(r'\b\d{2}/\d{2}/\d{4}\b', text)
    name = None
    lines = text.split('\n')
    for line in lines:
        if "Name:" in line:
            name_match = re.search(r'Name:\s*(.*)', line)
            if name_match:
                name = name_match.group(1).strip()
            break
    details = {
        'dob': dob.group() if dob else None,
        'name': name
    }
    return details

def find_name_and_dob_driving(text):
    dob = None
    name = None
    lines = text.split('\n')
    for line in lines:
        if "Name:" in line:
            name_match = re.search(r'Name:\s*(.*)', line)
            if name_match:
                name = name_match.group(1).strip()
        if "DOB:" in line or "Date of Birth:" in line:
            dob_match = re.search(r'\b\d{2}-\d{2}-\d{4}\b', line)
            if dob_match:
                dob = dob_match.group()
    details = {
        'dob': dob,
        'name': name
    }
    return details

def fetch_numbers_from_db(table_name, column_name):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="unnati",
        database="documentsverification"
    )
    cursor = db.cursor()
    cursor.execute(f"SELECT {column_name} FROM {table_name}")
    numbers = cursor.fetchall()
    cursor.close()
    db.close()
    return [str(num[0]) for num in numbers]

@app.route('/extract-details', methods=['POST'])
def extract_details():
    document_type = request.form.get('documenttype')
    file = request.files['document']
    file_extension = file.filename.split('.')[-1].lower()

    if not document_type:
        return jsonify({'error': 'Document type not provided'}), 400

    if document_type.lower() not in ['aadhar', 'pan', 'voter', 'dl']:
        return jsonify({'error': 'Unsupported document type'}), 400

    if document_type.lower() == 'aadhar':
        if file_extension in ['jpg', 'jpeg', 'png']:
            file.save('uploaded_image.' + file_extension)
            text = extract_text_from_image('uploaded_image.' + file_extension)
            os.remove('uploaded_image.' + file_extension)
        else:
            return jsonify({'error': 'Invalid file format for Aadhaar document'}), 400
        aadhar_numbers_db = fetch_numbers_from_db('aadhar_table', 'aadhar_number')
        aadhar_number = find_12_digit_number_with_spaces(text)
        if aadhar_number:
            details = find_name_and_dob_aadhar(text)
            details['number'] = aadhar_number
            details['found_in_db'] = aadhar_number in aadhar_numbers_db
            return jsonify({
                'document_type': 'Aadhaar',
                'details': details
            })
    elif document_type.lower() == 'pan':
        if file_extension in ['jpg', 'jpeg', 'png']:
            file.save('uploaded_image.' + file_extension)
            text = extract_text_from_image('uploaded_image.' + file_extension)
            os.remove('uploaded_image.' + file_extension)
        else:
            return jsonify({'error': 'Invalid file format for PAN card document'}), 400
        pan_numbers_db = fetch_numbers_from_db('pan_table', 'pan_number')
        pan_number = find_pan_number(text)
        if pan_number:
            details = find_name_and_dob_pan(text)
            details['number'] = pan_number
            details['found_in_db'] = pan_number in pan_numbers_db
            return jsonify({
                'document_type': 'PAN',
                'details': details
            })
    elif document_type.lower() == 'voter':
        if file_extension in ['jpg', 'jpeg', 'png']:
            file.save('uploaded_image.' + file_extension)
            text = extract_text_from_image('uploaded_image.' + file_extension)
            os.remove('uploaded_image.' + file_extension)
        else:
            return jsonify({'error': 'Invalid file format for Voter ID document'}), 400
        voter_id_numbers_db = fetch_numbers_from_db('voter_table', 'voter_number')
        voter_id_number = find_voter_id_number(text)
        if voter_id_number:
            details = find_name_and_dob_voter(text)
            details['number'] = voter_id_number
            details['found_in_db'] = voter_id_number in voter_id_numbers_db
            return jsonify({
                'document_type': 'Voter ID',
                'details': details
            })
    elif document_type.lower() == 'dl':
        if file_extension in ['jpg', 'jpeg', 'png','pdf']:
            file.save('uploaded_image.' + file_extension)
            text = extract_text_from_image('uploaded_image.' + file_extension)
            os.remove('uploaded_image.' + file_extension)
        else:
            return jsonify({'error': 'Invalid file format for  License document'}), 400
        driving_license_numbers_db = fetch_numbers_from_db('dl_table', 'dl_number')
        driving_license_number = find_driving_license_number(text)
        if driving_license_number:
            details = find_name_and_dob_driving(text)
            details['number'] = driving_license_number
            details['found_in_db'] = driving_license_number in driving_license_numbers_db
            return jsonify({
                'document_type': 'Driving License',
                'details': details
            })

    return jsonify({'error': f'No valid {document_type} document found in the request'}), 400

if __name__ == '__main__':
    app.run(debug=True)
