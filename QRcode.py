from flask import Flask, render_template, request
import qrcode
import os
from db import get_db

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        # Get user information from the form
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        start_place = request.form['start_place']
        end_place = request.form['end_place']
        date = request.form['date']
        time = request.form['time']

        # Create the data string for the QR code
        data = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nStart Place: {start_place}\nEnd Place: {end_place}\nDate: {date}\nTime: {time}"

        # Add error correction to the data using Reed-Solomon encoding
        # The error correction level can be set to 'L', 'M', 'Q', or 'H'
        # 'L' provides the least error correction and 'H' provides the most
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=10,
            border=5
        )
        # Convert the data string to bytes before adding to the QR code
        qr.add_data(data.encode('utf-8'))
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the image as a PNG file in the static directory
        filename = f"{name}_qr.png"
        filepath = os.path.join('static', filename)
        img.save(filepath)

        # Create a dictionary to store the QR generated credential
        qr_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'start_place': start_place,
            'end_place': end_place,
            'date': date,
            'time': time,
            'filename': filename
        }

        # Get a connection to the MongoDB database
        db = get_db()

        # Insert the QR generated credential into a collection
        collection = db['QRdata']
        collection.insert_one(qr_data)

        # Render the result page with the QR code image
        return render_template('result.html', filename=filename)

    except KeyError as e:
        # If a required form field is missing
        return render_template('form_error.html', message="Please fill in all required fields.")

    except Exception as e:
        # If any other exception occurs
        print("Error:", e)
        print("Form data:", request.form)
        return render_template('form_error.html', message="An error occurred while processing your request.")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500