import streamlit as st
from fpdf import FPDF
from datetime import datetime
import smtplib
from email.message import EmailMessage
from streamlit_drawable_canvas import st_canvas
import io

# --- PDF KLASSE ---
class AuditPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, '🦅 ADLER AUTOMOTIVE QUALITY', 0, 1, 'L')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, 'Professional Vehicle Logistics Auditing - VDI 2700 compliant', 0, 1, 'L')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def audit_line(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.cell(60, 8, f"{label}:", 0, 0)
        self.set_font('Arial', '', 10)
        self.cell(0, 8, str(value), 0, 1)

# --- MAIL FUNKTION ---
def sende_mail_mit_pdf(pdf_content, status_urteil, objekt_name):
    absender = "t.adler.1991@web.de"
    passwort = "mein_web_passwort" # <--- BITTE EINTRAGEN
    
    msg = EmailMessage()
    msg['Subject'] = f"Audit-Bericht: {status_urteil} - {objekt_name}"
    msg['From'] = absender
    msg['To'] = absender
    msg.set_content(f"Hallo Tobias,\n\nanbei der neue Audit-Bericht für {objekt_name}.\nStatus: {status_urteil}")
    
    msg.add_attachment(pdf_content, maintype='application', subtype='pdf', filename=f"Audit_{objekt_name}.pdf")
    
    with smtplib.SMTP("smtp.web.de", 587) as server:
        server.starttls()
        server.login(absender, passwort)
        server.send_message(msg)

# --- STREAMLIT UI ---
st.title("🦅 Adler Audit-Portal")

# Stammdaten
st.subheader("📋 Stammdaten")
c1, c2 = st.columns(2)
auftraggeber = c1.text_input("Auftraggeber", "ARS Altmann AG")
sub = c1.text_input("Subunternehmer")
lkw_kz = c2.text_input("Kennzeichen")
fahrer = c2.text_input("Fahrer Name")

# Technik & Lasi
st.divider()
st.subheader("🚛 LKW Technik & LaSi")
col_tech1, col_tech2 = st.columns(2)
vdi_m = col_tech1.radio("VDI Konform (Motorwagen)?", ["Ja", "Nein"])
vdi_a = col_tech2.radio("VDI Konform (Anhänger)?", ["Ja", "Nein"])
keile = st.number_input("Defekte Keile", 0)
gurte = st.number_input("Defekte Gurte", 0)

# Foto & Unterschrift
st.divider()
st.subheader("📸 Dokumentation & Unterschrift")
foto = st.camera_input("Mängelfoto aufnehmen")

st.write("Unterschrift Fahrer/Auditor:")
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0.3)",
    stroke_width=2,
    stroke_color="#000",
    background_color="#eee",
    height=150,
    key="canvas",
)

# Abschluss
st.divider()
urteil = st.selectbox("Gesamturteil", ["✅ POSITIV", "❌ NEGATIV"])
bemerkung = st.text_area("Schlussbemerkung")

if st.button("Audit finalisieren & Senden"):
    with st.spinner('Bericht wird erstellt...'):
        # PDF Daten sammeln
        daten = {
            'auftraggeber': auftraggeber, 'subunternehmer': sub,
            'kennzeichen': lkw_kz, 'fahrer': fahrer,
            'h_m': "VDI OK" if vdi_m=="Ja" else "VDI Mangel",
            'h_a': "VDI OK" if vdi_a=="Ja" else "VDI Mangel",
            'keile': keile, 'gurte': gurte, 'urteil': urteil
        }
        
        # PDF generieren
        pdf = AuditPDF()
        pdf.add_page()
        pdf.chapter_title("1. STAMMDATEN")
        for k, v in list(daten.items())[:4]: pdf.audit_line(k.capitalize(), v)
        pdf.chapter_title("2. TECHNIK & SICHERHEIT")
        for k, v in list(daten.items())[4:8]: pdf.audit_line(k.capitalize(), v)
        pdf.chapter_title("3. BEMERKUNG")
        pdf.multi_cell(0, 10, bemerkung)
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        
        # Senden
        try:
            sende_mail_mit_pdf(pdf_bytes, urteil, lkw_kz)
            st.success("Audit erfolgreich gesendet! 🦅")
            st.balloons()
        except Exception as e:
            st.error(f"Fehler: {e}")

