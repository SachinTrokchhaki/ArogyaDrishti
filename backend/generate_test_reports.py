from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'TitleStyle', parent=styles['Title'],
    fontSize=18, textColor=colors.HexColor('#003366'), spaceAfter=6
)
heading_style = ParagraphStyle(
    'HeadingStyle', parent=styles['Heading2'],
    fontSize=13, textColor=colors.HexColor('#005599'), spaceAfter=6
)
normal_style = ParagraphStyle(
    'NormalStyle', parent=styles['Normal'],
    fontSize=10, leading=14
)
small_style = ParagraphStyle(
    'SmallStyle', parent=styles['Normal'],
    fontSize=9, textColor=colors.grey
)


def make_table(data, col_widths=None):
    table = Table(data, colWidths=col_widths, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005599')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F4F8')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


# ============================================================
# REPORT 1: CBC
# ============================================================
def build_report_1():
    elements = []
    elements.append(Paragraph("CITY DIAGNOSTIC CENTER", title_style))
    elements.append(Paragraph("Complete Blood Count (CBC) Report", heading_style))
    elements.append(Spacer(1, 8))

    info = [
        ["Patient Name:", "Sunita Rai", "Age:", "32 years"],
        ["Gender:", "Female", "Date:", "10/08/2024"],
        ["Lab No.:", "CBC-2024-1187", "Referred By:", "Dr. A. K. Verma"],
    ]
    info_table = Table(info, colWidths=[1.1*inch, 2.0*inch, 1.1*inch, 1.8*inch])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 14))

    data = [
        ["Test Name", "Result", "Unit", "Reference Range"],
        ["Hemoglobin", "10.2", "g/dL", "12.0 - 15.0"],
        ["Total Leucocyte Count (TLC)", "11200", "cells/cumm", "4000 - 11000"],
        ["Neutrophils", "72", "%", "40 - 70"],
        ["Lymphocytes", "20", "%", "20 - 40"],
        ["Eosinophils", "4", "%", "1 - 6"],
        ["Monocytes", "3", "%", "2 - 8"],
        ["Basophils", "1", "%", "0 - 2"],
        ["Platelet Count", "1.20", "Lakh/cumm", "1.50 - 4.50"],
        ["RBC Count", "3.85", "million/cumm", "4.20 - 5.60"],
        ["PCV (Hematocrit)", "32.5", "%", "40 - 50"],
        ["MCV", "78.0", "fL", "80 - 96"],
        ["MCH", "25.4", "pg", "27 - 32"],
        ["MCHC", "31.2", "g/dL", "32 - 36"],
        ["RDW-CV", "16.8", "%", "11.5 - 14.5"],
    ]
    elements.append(make_table(data, col_widths=[2.4*inch, 1.0*inch, 1.3*inch, 1.6*inch]))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("Interpretation", heading_style))
    elements.append(Paragraph(
        "Low hemoglobin and RBC count – suggestive of anemia.<br/>"
        "Low platelet count – thrombocytopenia.<br/>"
        "High TLC with neutrophilia – possible infection.<br/>"
        "<b>Impression:</b> Microcytic hypochromic anemia with thrombocytopenia "
        "and leukocytosis. Clinical correlation and further evaluation advised.",
        normal_style
    ))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Pathologist: Dr. S. Maharjan", normal_style))
    elements.append(Paragraph("Signature: ____________________", normal_style))
    return elements


# ============================================================
# REPORT 2: X-RAY
# ============================================================
def build_report_2():
    elements = []
    elements.append(Paragraph("NATIONAL MEDICAL INSTITUTE", title_style))
    elements.append(Paragraph("Radiology Report – X-ray Chest (PA View)", heading_style))
    elements.append(Spacer(1, 8))

    info = [
        ["Patient Name:", "Rajesh Kumar Yadav", "Age:", "45 years"],
        ["Gender:", "Male", "Date:", "22/07/2024"],
        ["Referred By:", "Dr. P. K. Jha", "Film No.:", "XR-2024-4415"],
    ]
    info_table = Table(info, colWidths=[1.1*inch, 2.0*inch, 1.1*inch, 1.8*inch])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("Clinical Indication", heading_style))
    elements.append(Paragraph("Chronic cough, shortness of breath.", normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Findings", heading_style))
    for f in [
        "Bilateral lung fields show increased bronchovascular markings.",
        "No focal consolidation or cavitary lesion seen.",
        "No pleural effusion or pneumothorax.",
        "Cardiothoracic ratio is within normal limits.",
        "Bilateral costophrenic angles are clear.",
        "Bony cage and soft tissues are unremarkable.",
        "No mediastinal widening.",
    ]:
        elements.append(Paragraph(f"• {f}", normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Impression", heading_style))
    for i in [
        "Prominent bronchovascular markings – suggestive of chronic bronchitis.",
        "No active lung parenchymal lesion.",
        "No pleural effusion or pneumothorax.",
    ]:
        elements.append(Paragraph(f"• {i}", normal_style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Radiologist: Dr. M. K. Singh", normal_style))
    elements.append(Paragraph("Signature: ____________________", normal_style))
    return elements


# ============================================================
# REPORT 3: DISCHARGE SUMMARY
# ============================================================
def build_report_3():
    elements = []
    elements.append(Paragraph("CITY CARE HOSPITAL", title_style))
    elements.append(Paragraph("Discharge Summary – Obstetrics & Gynecology", heading_style))
    elements.append(Spacer(1, 8))

    info = [
        ["Patient Name:", "Priya Sharma", "Age:", "28 years"],
        ["Gender:", "Female", "Admission Date:", "05/06/2024"],
        ["Discharge Date:", "09/06/2024", "IPD No.:", "IPD-2024-0921"],
    ]
    info_table = Table(info, colWidths=[1.2*inch, 1.9*inch, 1.3*inch, 1.6*inch])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 14))

    sections = [
        ("Chief Complaints", [
            "Lower abdominal pain x 2 days",
            "Fever x 1 day",
            "Nausea and vomiting",
        ]),
        ("History of Present Illness", [
            "Patient was apparently well 2 days back when she developed lower "
            "abdominal pain, gradually increasing in intensity, associated with "
            "fever and vomiting. No history of bleeding per vaginum, no urinary complaints."
        ]),
        ("Past History", [
            "No known chronic illness.",
            "No previous surgery.",
            "Menstrual cycle: regular.",
        ]),
        ("Examination on Admission", [
            "BP: 110/70 mmHg",
            "Pulse: 96/min",
            "Temp: 101.2°F",
            "SpO2: 97% on room air",
            "Abdomen: tender in lower abdomen, no guarding/rigidity",
            "Pelvic examination: cervix healthy, no bleeding",
        ]),
    ]
    for title, items in sections:
        elements.append(Paragraph(title, heading_style))
        for it in items:
            elements.append(Paragraph(f"• {it}", normal_style))
        elements.append(Spacer(1, 8))

    elements.append(Paragraph("Investigations", heading_style))
    inv_data = [
        ["Test", "Result", "Reference Range"],
        ["Hemoglobin", "11.5 g/dL", "12.0 - 15.0"],
        ["TLC", "13500 cells/cumm", "4000 - 11000"],
        ["Platelet Count", "2.10 Lakh/cumm", "1.50 - 4.50"],
        ["CRP", "18 mg/L", "< 5"],
        ["Urine Routine", "Pus cells 10-12/hpf", "0-5/hpf"],
        ["USG Pelvis", "Mild free fluid in pelvis", "—"],
    ]
    elements.append(make_table(inv_data, col_widths=[1.8*inch, 2.4*inch, 2.1*inch]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Course in Hospital", heading_style))
    elements.append(Paragraph(
        "Patient was managed conservatively with IV antibiotics, IV fluids, "
        "analgesics, and antiemetics. Fever subsided after 48 hours. Pain reduced "
        "gradually. Repeat TLC showed decreasing trend. Patient improved "
        "symptomatically and was discharged in stable condition.", normal_style
    ))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Diagnosis at Discharge", heading_style))
    elements.append(Paragraph("• Pelvic Inflammatory Disease (PID)", normal_style))
    elements.append(Paragraph("• Urinary Tract Infection (UTI)", normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Discharge Medications", heading_style))
    meds = [
        "Tab. Cefixime 200 mg – 1 tablet twice daily x 5 days",
        "Tab. Metronidazole 400 mg – 1 tablet three times daily x 5 days",
        "Tab. Paracetamol 500 mg – 1 tablet SOS for pain/fever",
        "Tab. Pantoprazole 40 mg – 1 tablet before breakfast x 5 days",
        "Tab. Multivitamin – 1 tablet once daily x 10 days",
    ]
    for m in meds:
        elements.append(Paragraph(f"• {m}", normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Advice", heading_style))
    for a in [
        "Complete rest for 1 week.",
        "Drink plenty of water.",
        "Avoid sexual intercourse until follow-up.",
        "Maintain personal hygiene.",
        "Follow-up in OPD after 1 week.",
        "Return immediately if fever, severe pain, or bleeding occurs.",
    ]:
        elements.append(Paragraph(f"• {a}", normal_style))

    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Discharged by: Dr. N. K. Gupta", normal_style))
    elements.append(Paragraph("Signature: ____________________", normal_style))
    return elements


# ============================================================
# GENERATE 3 SEPARATE PDFs
# ============================================================
def generate_pdf(filename, builder):
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        topMargin=0.7*inch, bottomMargin=0.7*inch,
        leftMargin=0.8*inch, rightMargin=0.8*inch,
        title=filename
    )
    doc.build(builder())
    print(f"✅ Created: {filename}")


if __name__ == "__main__":
    generate_pdf("Report1_CBC.pdf", build_report_1)
    generate_pdf("Report2_Xray.pdf", build_report_2)
    generate_pdf("Report3_DischargeSummary.pdf", build_report_3)
    print("\n🎉 All 3 PDF reports generated successfully!")
