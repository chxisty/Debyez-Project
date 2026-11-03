"""
AEGIS SERIES-7: FINAL PROJECT REPORT GENERATOR
Produces the official assessment deliverable for Debyez Technologies Pvt. Ltd.:
1. AEGIS_SERIES7_FINAL_PROJECT_REPORT.docx (Editable Source)
2. AEGIS_SERIES7_FINAL_PROJECT_REPORT.pdf (Native PDF via Word COM Automation, < 10 MB)
"""

import os
import sys
import json
import sqlite3
import datetime
from PIL import Image

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# --- Color Palette Constants ---
NAVY_PRIMARY = RGBColor(26, 54, 93)     # #1A365D - Deep Navy
BLUE_SECONDARY = RGBColor(43, 108, 176) # #2B6CB0 - Slate Blue
CHARCOAL_BODY = RGBColor(45, 55, 72)    # #2D3748 - Charcoal Text
MUTED_GREY = RGBColor(113, 128, 150)    # #718096 - Muted Grey
WHITE = RGBColor(255, 255, 255)
GREEN_ACCENT = RGBColor(40, 167, 69)

HEX_NAVY = "1A365D"
HEX_LIGHT_BLUE = "EBF8FF"
HEX_LIGHT_GREY = "F7FAFC"
HEX_BORDER_GREY = "CBD5E0"
HEX_HEADER_BG = "1A365D"
HEX_CALLOUT_BORDER = "2B6CB0"

# --- XML Helper Functions ---

def set_cell_background(cell, hex_color):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    # Remove existing shading if present
    for child in list(tcPr):
        if child.tag.endswith('shd'):
            tcPr.remove(child)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    """Sets inner margins (padding) of a table cell in dxa."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_borders(cell, top="CBD5E0", bottom="CBD5E0", left=None, right=None, sz="4"):
    """Sets cell borders."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for border_name, color in borders.items():
        if color:
            b = OxmlElement(f'w:{border_name}')
            b.set(qn('w:val'), 'single')
            b.set(qn('w:sz'), sz)
            b.set(qn('w:space'), '0')
            b.set(qn('w:color'), color)
            tcBorders.append(b)
        else:
            b = OxmlElement(f'w:{border_name}')
            b.set(qn('w:val'), 'none')
            tcBorders.append(b)
    tcPr.append(tcBorders)

def add_footer_field(run, field_name):
    """Inserts a dynamic Word field like PAGE or NUMPAGES."""
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = field_name
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    
    r = run._r
    r.append(fldChar1)
    r.append(instrText)
    r.append(fldChar2)
    r.append(fldChar3)

def format_paragraph(p, space_before=0, space_after=6, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = align

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    format_paragraph(p, space_before=20, space_after=8, align=WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = NAVY_PRIMARY
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    format_paragraph(p, space_before=14, space_after=6, align=WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = BLUE_SECONDARY
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    format_paragraph(p, space_before=10, space_after=4, align=WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = CHARCOAL_BODY
    return p

def add_body_p(doc, text):
    p = doc.add_paragraph()
    format_paragraph(p, space_before=0, space_after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.color.rgb = CHARCOAL_BODY
    return p

def add_bullet_p(doc, bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    format_paragraph(p, space_before=2, space_after=4, align=WD_ALIGN_PARAGRAPH.LEFT)
    run_b = p.add_run(bold_prefix)
    run_b.font.name = 'Times New Roman'
    run_b.font.size = Pt(11)
    run_b.font.bold = True
    run_b.font.color.rgb = NAVY_PRIMARY
    
    run_t = p.add_run(text)
    run_t.font.name = 'Times New Roman'
    run_t.font.size = Pt(11)
    run_t.font.color.rgb = CHARCOAL_BODY
    return p

def add_callout(doc, title, text, border_color="2B6CB0", bg_color="EBF8FF"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.27)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    set_cell_borders(cell, top="CBD5E0", bottom="CBD5E0", left=border_color, right="CBD5E0", sz="16")
    
    p = cell.paragraphs[0]
    format_paragraph(p, space_before=0, space_after=4, align=WD_ALIGN_PARAGRAPH.LEFT)
    run_title = p.add_run(title + "\n")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(11)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY_PRIMARY
    
    run_text = p.add_run(text)
    run_text.font.name = 'Times New Roman'
    run_text.font.size = Pt(10.5)
    run_text.font.italic = True
    run_text.font.color.rgb = CHARCOAL_BODY
    
    # Empty space after table
    p_after = doc.add_paragraph()
    format_paragraph(p_after, space_before=0, space_after=6)

def add_figure(doc, image_path, fig_num, caption, explanation=None):
    if not os.path.exists(image_path):
        print(f"Warning: Figure image not found: {image_path}")
        return
    
    p_img = doc.add_paragraph()
    format_paragraph(p_img, space_before=10, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    run_img = p_img.add_run()
    run_img.add_picture(image_path, width=Inches(6.1))
    
    p_cap = doc.add_paragraph()
    format_paragraph(p_cap, space_before=2, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    p_cap.paragraph_format.keep_with_next = True
    run_num = p_cap.add_run(f"Figure {fig_num}: ")
    run_num.font.name = 'Times New Roman'
    run_num.font.size = Pt(10)
    run_num.font.bold = True
    run_num.font.color.rgb = NAVY_PRIMARY
    
    run_cap = p_cap.add_run(caption)
    run_cap.font.name = 'Times New Roman'
    run_cap.font.size = Pt(10)
    run_cap.font.italic = True
    run_cap.font.color.rgb = CHARCOAL_BODY
    
    if explanation:
        p_exp = doc.add_paragraph()
        format_paragraph(p_exp, space_before=2, space_after=10, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        run_exp = p_exp.add_run(f"Technical Analysis: {explanation}")
        run_exp.font.name = 'Times New Roman'
        run_exp.font.size = Pt(9.5)
        run_exp.font.color.rgb = MUTED_GREY

def create_styled_table(doc, headers, data, col_widths=None):
    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Repeat header row across pages
    header_tr = tbl.rows[0]._tr.get_or_add_trPr()
    header_tr.append(OxmlElement('w:tblHeader'))
    
    # Format Header Row
    for idx, heading in enumerate(headers):
        cell = tbl.rows[0].cells[idx]
        if col_widths and idx < len(col_widths):
            cell.width = col_widths[idx]
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell, top=140, bottom=140, left=160, right=160)
        set_cell_borders(cell, top="1A365D", bottom="1A365D", left=None, right=None, sz="8")
        
        p = cell.paragraphs[0]
        format_paragraph(p, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.LEFT)
        run = p.add_run(heading)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = WHITE
        
    # Format Data Rows
    for row_idx, row_data in enumerate(data):
        row = tbl.rows[row_idx + 1]
        # Prevent row split across pages
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))
        
        bg_col = HEX_LIGHT_GREY if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_data):
            cell = row.cells[col_idx]
            if col_widths and col_idx < len(col_widths):
                cell.width = col_widths[col_idx]
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            set_cell_borders(cell, top="E2E8F0", bottom="E2E8F0", left=None, right=None, sz="4")
            
            p = cell.paragraphs[0]
            format_paragraph(p, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.LEFT)
            run = p.add_run(str(cell_value))
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)
            run.font.color.rgb = CHARCOAL_BODY
            
    # Add spacing after table
    p_after = doc.add_paragraph()
    format_paragraph(p_after, space_before=0, space_after=8)
    return tbl

print("Helper formatting functions defined successfully.")
