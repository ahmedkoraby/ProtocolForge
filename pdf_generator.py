
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import qrcode

def generate_qr_code(text, size=2):
    """Generate QR code image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer

def generate_protocol_pdf(compound_name, stock_mM, top_dose_uM, dilution_factor=3, num_points=8):
    """Generate professional PDF dilution protocol with QR code"""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, 
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1f77b4'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    # Header with logo
    header_data = [
        [Paragraph("🧬 <b>ProtocolForge</b>", title_style)],
        [Paragraph("Automated Dilution Protocol Generator", subtitle_style)]
    ]
    header_table = Table(header_data, colWidths=[7*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Horizontal line
    story.append(Table([['']], colWidths=[7*inch], 
                      style=TableStyle([('LINEBELOW', (0, 0), (0, 0), 2, colors.HexColor('#1f77b4'))])))
    story.append(Spacer(1, 0.15*inch))
    
    # Compound info section
    now = datetime.now()
    comp_info_data = [
        ['Compound Name', compound_name, 'Date', now.strftime('%Y-%m-%d')],
        ['Stock Concentration', f'{stock_mM} mM', 'Time', now.strftime('%H:%M:%S')],
        ['Top Dose', f'{top_dose_uM} µM', 'Final Volume', '450 µL'],
        ['Dilution Factor', f'{dilution_factor}×', 'Points', str(num_points)],
    ]
    
    comp_table = Table(comp_info_data, colWidths=[1.5*inch, 1.8*inch, 1.5*inch, 1.7*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Dilution series table
    story.append(Paragraph("Dilution Series (Constant DMSO @ 0.2%)", header_style))
    
    doses = []
    for i in range(num_points):
        dose = top_dose_uM / (dilution_factor ** i)
        doses.append(dose)
    doses = sorted(doses, reverse=True)
    
    final_vol = 450  # µL
    
    table_data = [
        ['Tube', 'Dose (µM)', 'Dose (nM)', 'Compound Vol (µL)', 'Extra DMSO (µL)', 'Diluent (µL)']
    ]
    
    for idx, dose in enumerate(doses, 1):
        compound_vol = (dose * final_vol) / (stock_mM * 1000)
        dmso_from_compound = (compound_vol / final_vol) * 100
        extra_dmso_vol = max(0, (0.2 - dmso_from_compound) * final_vol / 100)
        diluent_vol = final_vol - compound_vol - extra_dmso_vol
        
        table_data.append([
            f"T{idx}",
            f"{dose:.3e}" if dose >= 1 else f"{dose:.2e}",
            f"{dose*1000:.1f}" if dose >= 0.001 else f"{dose*1000:.2e}",
            f"{compound_vol:.3f}",
            f"{extra_dmso_vol:.2f}",
            f"{diluent_vol:.1f}"
        ])
    
    table = Table(table_data, colWidths=[0.6*inch, 1.0*inch, 1.0*inch, 1.2*inch, 1.1*inch, 1.1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Important notes section
    story.append(Paragraph("Important Notes", header_style))
    notes_text = f"""
    <b>DMSO Matching:</b> All tubes maintain constant DMSO at 0.2% to prevent solvent-based artifacts.<br/>
    <b>Pipetting Safety:</b> All volumes are designed to be easily pipettable (≥0.1 µL).<br/>
    <b>Storage:</b> Store stock solution at 4°C in sealed, labeled tubes. Stability: 2-6 months.<br/>
    <b>Solvent:</b> Stock is prepared in 100% DMSO. Diluent is culture media or PBS as appropriate.
    """
    story.append(Paragraph(notes_text, styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    # Footer section with QR code
    footer_data = [
        [
            Paragraph("<b>Generated by ProtocolForge</b><br/>Ahmed K. Oraby<br/>University of Alberta", 
                     styles['Normal']),
            Paragraph("<b>Ref:</b> " + now.strftime('%Y%m%d_%H%M%S'), styles['Normal']),
            'QR Code'
        ]
    ]
    
    try:
        qr_buffer = generate_qr_code(f"ProtocolForge_{compound_name}_{now.strftime('%Y%m%d_%H%M%S')}")
        qr_img = Image(qr_buffer, width=0.8*inch, height=0.8*inch)
        footer_data[0][2] = qr_img
    except:
        footer_data[0][2] = Paragraph("(QR Code)", styles['Normal'])
    
    footer_table = Table(footer_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(Table([['']], colWidths=[7*inch], 
                      style=TableStyle([('LINEABOVE', (0, 0), (0, 0), 1, colors.HexColor('#cccccc'))])))
    story.append(Spacer(1, 0.1*inch))
    story.append(footer_table)
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer

def generate_batch_protocol_pdf(compounds_list):
    """Generate batch PDF with all compounds (one per page)"""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1f77b4'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    now = datetime.now()
    
    # Title page
    story.append(Paragraph("🧬 ProtocolForge", title_style))
    story.append(Paragraph("Batch Dilution Protocol Compilation", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    summary_text = f"""
    <b>Generated:</b> {now.strftime('%Y-%m-%d %H:%M:%S')}<br/>
    <b>Compounds:</b> {len(compounds_list)}<br/>
    <b>Prepared by:</b> Ahmed K. Oraby, University of Alberta<br/>
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Summary table
    story.append(Paragraph("Compound Summary", header_style))
    summary_data = [['#', 'Compound', 'Stock (mM)', 'Top Dose (µM)', 'Notes']]
    for idx, compound in enumerate(compounds_list, 1):
        summary_data.append([
            str(idx),
            compound.get('Compound', 'Unknown'),
            str(compound.get('Stock_mM', 50)),
            str(compound.get('Top_Dose_uM', 100)),
            compound.get('Notes', '')[:30]
        ])
    
    summary_table = Table(summary_data, colWidths=[0.4*inch, 2.0*inch, 1.2*inch, 1.3*inch, 2.1*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    story.append(summary_table)
    story.append(PageBreak())
    
    # Individual protocols
    for compound in compounds_list:
        stock_mM = compound.get('Stock_mM', 50)
        top_dose_uM = compound.get('Top_Dose_uM', 100)
        comp_name = compound.get('Compound', 'Unknown')
        
        story.append(Paragraph(f"Protocol: {comp_name}", title_style))
        story.append(Spacer(1, 0.1*inch))
        
        comp_info_data = [
            ['Stock Concentration', f'{stock_mM} mM', 'Final Volume', '450 µL'],
            ['Top Dose', f'{top_dose_uM} µM', 'Dilution Factor', '3×'],
        ]
        
        comp_table = Table(comp_info_data, colWidths=[2.0*inch, 1.5*inch, 2.0*inch, 1.5*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ]))
        story.append(comp_table)
        story.append(Spacer(1, 0.15*inch))
        
        # Dilution table for each compound
        story.append(Paragraph("Dilution Series", header_style))
        
        doses = []
        for i in range(8):
            dose = top_dose_uM / (3 ** i)
            doses.append(dose)
        doses = sorted(doses, reverse=True)
        
        final_vol = 450
        
        table_data = [['Tube', 'Dose (µM)', 'Dose (nM)', 'Stock (µL)', 'Media (µL)']]
        
        for idx, dose in enumerate(doses, 1):
            compound_vol = (dose * final_vol) / (stock_mM * 1000)
            media_vol = final_vol - compound_vol
            
            table_data.append([
                f"T{idx}",
                f"{dose:.2e}",
                f"{dose*1000:.1f}",
                f"{compound_vol:.2f}",
                f"{media_vol:.1f}"
            ])
        
        table = Table(table_data, colWidths=[0.7*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer
