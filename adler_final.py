import streamlit as st
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from streamlit_drawable_canvas import st_canvas
import datetime

# 1. Seiteneinstellungen für das iPhone (Emoji als Icon)
st.set_page_config(page_title="Adler Audit", page_icon="🦅", layout="centered")

# 2. Sicherheit: Passwort aus den Streamlit Secrets laden
# (Stelle sicher, dass du 'mein_web_passwort' in den Streamlit Settings hinterlegt hast!)
try:
    ABSENDER_PASSWORT = st.secrets["mein_web_passwort"]
except:
    ABSENDER_PASSWORT = "PASSWORT_NICHT_GEFUNDEN"

# Konfiguration des E-Mail-Versands
ABSENDER_EMAIL = "t.adler.1991@web.de"
EMPFAENGER_EMAIL = "t.adler.1991@web.de"
SMTP_SERVER = "smtp.web.de"
SMTP_PORT = 587

def send_email(file_path, subject):
    msg = MIMEMultipart()
    msg['From'] = ABSENDER_EMAIL
    msg['To'] = EMPFAENGER_EMAIL
    msg['Subject'] = subject
    
    body = "Anbei erhalten Sie das ausgefüllte LKW-Audit-Protokoll der Firma Adler."
    msg.attach(MIMEText(body, 'plain'))
    
    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {file_path}")
        msg.attach(part)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(ABSENDER_EMAIL, ABSENDER_PASSWORT)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Versand: {e}")
        return False

# UI der App
st.title("🦅 Adler LKW-Audit")
st.write("Bitte füllen Sie die Checkliste für die Abfahrtskontrolle aus.")

with st.form("audit_form"):
    datum = st.date_input("Datum", datetime.date.today())
    kennzeichen = st.text_input("LKW Kennzeichen")
    fahrer = st.text_input("Name des Fahrers")
    
    st.subheader("Checkliste")
    licht = st.checkbox("Beleuchtung (OK)")
    reifen = st.checkbox("Reifen & Luftdruck (OK)")
    bremsen = st.checkbox("Bremsanlage (OK)")
    ladungs = st.checkbox("Ladungssicherung (OK)")
    
    bemerkung = st.text_area("Bemerkungen / Mängel")
    
    st.subheader("Unterschrift")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#eeeeee",
        height=150,
        key="canvas",
    )
    
    submit = st.form_submit_button("Audit abschließen & PDF senden")

if submit:
    if not kennzeichen or not fahrer:
        st.warning("Bitte Kennzeichen und Fahrer angeben!")
    else:
        # PDF Erstellung
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "LKW-Audit Protokoll - Firma Adler", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Datum: {datum}", ln=True)
        pdf.cell(200, 10, f"Kennzeichen: {kennzeichen}", ln=True)
        pdf.cell(200, 10, f"Fahrer: {fahrer}", ln=True)
        pdf.ln(5)
        
        pdf.cell(200, 10, f"Beleuchtung: {'OK' if licht else 'Mangelhaft'}", ln=True)
        pdf.cell(200, 10, f"Reifen: {'OK' if reifen else 'Mangelhaft'}", ln=True)
        pdf.cell(200, 10, f"Bremsen: {'OK' if bremsen else 'Mangelhaft'}", ln=True)
        pdf.cell(200, 10, f"Ladungssicherung: {'OK' if ladungs else 'Mangelhaft'}", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"Bemerkungen: {bemerkung}")
        
        filename = f"Audit_{kennzeichen}_{datum}.pdf"
        pdf.output(filename)
        
        if send_email(filename, f"LKW Audit - {kennzeichen}"):
            st.success(f"Audit erfolgreich gesendet an {EMPFAENGER_EMAIL}!")
            st.balloons()
