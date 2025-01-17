from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os

# Flask Application Configuration
app = Flask(__name__)
app.secret_key = 'secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Constants
FONT_NAME = "Helvetica"
FONT_SIZE = 12
FONT_BOLD = "Helvetica-Bold"
PDF_TITLE = "Curriculum Vitae"

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
	os.makedirs(UPLOAD_FOLDER)


# Helper function to extract form data
def extract_form_data(request):
	return {
		"Full Name": request.form.get("fullName"),
		"Email": request.form.get("email"),
		"Skills": request.form.get("skills"),
		"Languages": request.form.get("languages"),
		"Experience": request.form.get("experience"),
		"References": request.form.get("references"),
		"Certifications": request.form.get("certifications"),
		"Achievements": request.form.get("achievements"),
		"Hobbies": request.form.get("hobbies"),
	}


# Function to create PDF
def create_pdf(user_info, profile_picture=None):
	pdf_buffer = BytesIO()
	pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

	# Add Title
	pdf.setFont(FONT_BOLD, 16)
	pdf.drawCentredString(300, 750, PDF_TITLE)

	# Add Profile Picture
	if profile_picture:
		pdf.drawImage(ImageReader(profile_picture), 450, 600, width=100, height=100)

	# Add User Information
	y_position = 700
	pdf.setFont(FONT_NAME, FONT_SIZE)
	for key, value in user_info.items():
		pdf.drawString(50, y_position, f"{key}: {value}")
		y_position -= 20

	pdf.save()
	pdf_buffer.seek(0)
	return pdf_buffer


# Main route
@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "POST":
		# Extract form data
		user_info = extract_form_data(request)

		# Handle profile picture upload
		profile_picture = request.files.get("profilePicture")
		profile_pic_path = None
		if profile_picture and profile_picture.filename:
			filename = secure_filename(profile_picture.filename)
			profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			profile_picture.save(profile_pic_path)

		# Generate and return the PDF
		pdf_buffer = create_pdf(user_info, profile_pic_path)
		return send_file(
			pdf_buffer,
			as_attachment=True,
			download_name="cv.pdf",
			mimetype="application/pdf"
		)

	return render_template("index.html")


if __name__ == "__main__":
	app.run(debug=True)