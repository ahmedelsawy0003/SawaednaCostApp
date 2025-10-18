"""
Utility functions for PDF generation
"""

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from datetime import datetime


def generate_material_request_pdf(material_request):
    """
    Generate PDF for Material Request
    
    Args:
        material_request: MaterialRequest object
        
    Returns:
        BytesIO: PDF file in memory
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_RIGHT
    )
    
    # Title
    title = Paragraph("طلب توريد مواد", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Header information
    header_data = [
        ['رقم الطلب:', material_request.request_number, 'تاريخ تقديم الطلب:', 
         material_request.request_date.strftime('%Y-%m-%d') if material_request.request_date else ''],
        ['اسم المشروع:', material_request.project.name if material_request.project else '', '', ''],
        ['مقدم الطلب:', material_request.requester.username if material_request.requester else '',
         'مدير المشروع:', material_request.project_manager.username if material_request.project_manager else '']
    ]
    
    header_table = Table(header_data, colWidths=[3*cm, 6*cm, 3*cm, 4*cm])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 1*cm))
    
    # Items table
    table_data = [
        ['م', 'رقم البند', 'اسم المادة', 'الوحدة', 'الكمية المتاحة', 'الكمية المطلوبة', 'تاريخ التوريد']
    ]
    
    for idx, item in enumerate(material_request.items.all(), 1):
        table_data.append([
            str(idx),
            item.boq_item_number or '',
            item.material_name,
            item.unit,
            str(item.quantity_available),
            str(item.quantity_requested),
            item.required_date.strftime('%Y-%m-%d') if item.required_date else ''
        ])
    
    items_table = Table(table_data, colWidths=[1*cm, 2*cm, 6*cm, 2*cm, 2*cm, 2*cm, 2*cm])
    items_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 1*cm))
    
    # Notes
    if material_request.notes:
        notes = Paragraph(f"<b>ملاحظات:</b> {material_request.notes}", header_style)
        elements.append(notes)
        elements.append(Spacer(1, 1*cm))
    
    # Signatures
    sig_data = [
        ['توقيع مقدم الطلب:', '_________________', 'توقيع مدير المشروع:', '_________________']
    ]
    sig_table = Table(sig_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(sig_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_material_return_pdf(material_return):
    """
    Generate PDF for Material Return
    
    Args:
        material_return: MaterialReturn object
        
    Returns:
        BytesIO: PDF file in memory
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_RIGHT
    )
    
    # Title
    title = Paragraph("مرتجع مواد", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Header information
    header_data = [
        ['رقم الطلب:', material_return.return_number, 'تاريخ تقديم الطلب:', 
         material_return.return_date.strftime('%Y-%m-%d') if material_return.return_date else ''],
        ['اسم المشروع:', material_return.project.name if material_return.project else '', '', ''],
        ['مقدم الطلب:', material_return.requester.username if material_return.requester else '',
         'مدير المشروع:', material_return.project_manager.username if material_return.project_manager else '']
    ]
    
    header_table = Table(header_data, colWidths=[3*cm, 6*cm, 3*cm, 4*cm])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 1*cm))
    
    # Items table
    table_data = [
        ['م', 'رقم البند', 'اسم المادة', 'الوحدة', 'الكمية', 'الملاحظات']
    ]
    
    for idx, item in enumerate(material_return.items.all(), 1):
        table_data.append([
            str(idx),
            item.boq_item_number or '',
            item.material_name,
            item.unit,
            str(item.quantity),
            item.notes or ''
        ])
    
    items_table = Table(table_data, colWidths=[1*cm, 2*cm, 5*cm, 2*cm, 2*cm, 5*cm])
    items_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 1*cm))
    
    # Notes
    if material_return.notes:
        notes = Paragraph(f"<b>ملاحظات:</b> {material_return.notes}", header_style)
        elements.append(notes)
        elements.append(Spacer(1, 1*cm))
    
    # Signatures
    sig_data = [
        ['توقيع مقدم الطلب:', '_________________', 'توقيع مدير المشروع:', '_________________']
    ]
    sig_table = Table(sig_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(sig_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_payment_order_pdf(payment_order):
    """
    Generate PDF for Payment Order
    
    Args:
        payment_order: PaymentOrder object
        
    Returns:
        BytesIO: PDF file in memory
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    # Title
    title = Paragraph("أمر صرف", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Information table
    info_data = [
        ['رقم الأمر:', payment_order.payment_number, 'التاريخ:', 
         payment_order.payment_date.strftime('%Y-%m-%d') if payment_order.payment_date else ''],
        ['المشروع:', payment_order.project.name if payment_order.project else '', '', ''],
        ['نوع الصرف:', payment_order.payment_type_arabic, 'المستفيد:', payment_order.beneficiary],
        ['المبلغ:', f"{payment_order.amount:,.2f} ريال", 'الحالة:', payment_order.status_arabic],
        ['الوصف:', payment_order.description or '', '', '']
    ]
    
    info_table = Table(info_data, colWidths=[3*cm, 6*cm, 3*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 2*cm))
    
    # Signatures
    sig_data = [
        ['مقدم الطلب:', '_________________', 'المعتمد:', '_________________', 'المنفذ:', '_________________']
    ]
    sig_table = Table(sig_data, colWidths=[3*cm, 3*cm, 2*cm, 3*cm, 2*cm, 3*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(sig_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

