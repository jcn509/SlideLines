import PyPDF2
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import re

import argparse

"""A simple tool that adds a new page after every existing page in a given PDF that just contains lines. 
Very useful for printing out lecture slides with space to add your own notes.
"""

def get_lines_page(width: float, height:float, num_lines:int=12, horiz_margin:float=0, vert_margin:float=0,line_thickness:float=1) -> PyPDF2.pdf.PageObject:
    """
    Args:
        width (float): the width of the page
        height (float): the height of the page
        num_lines (int): the number of lines to be added to the page
        horiz_margin (float): the space to leave at either side of each line
        vertical_margin (float): the gap to leave between the bottom/top of the page and the first/last line
        line_thickness (float): the thickness of each line
        

    Returns:
        A PDF page with lines on it for use with PyPDF2

    """
    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=(width,height))
    can.setLineWidth(line_thickness)
    line_y = vert_margin + line_thickness
    line_gap = height / num_lines
    while line_y < height - (line_thickness + vert_margin):
        can.line(horiz_margin, line_y, width - horiz_margin, line_y)
        line_y += line_gap
    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)

    lines_pdf = PyPDF2.PdfFileReader(packet)
    return lines_pdf.getPage(0)
    


def add_lines_pages(in_file: PyPDF2.PdfFileReader, num_lines:int=12, horiz_margin:float=0, vert_margin:float=0,line_thickness:float=1) -> PyPDF2.PdfFileWriter:
    """Takes a PDF and adds a new page after each page that just contains lines
    
    Args:
        in_file (PyPDF2.PdfFileReader): the PyPDF2.PdfFileReader for the PDF to which lines are to be added
        num_lines (int): the number of lines to be added to each page
        horiz_margin (float): the space to leave at either side of each line
        vertical_margin (float): the gap to leave between the bottom/top of each page and the first/last line
        line_thickness (float): the thickness of each line

    Returns:
        PyPDF2.PdfFileWriter: the PyPDF2.PdfFileWriter for the new PDF

    """

    media_box = in_file.getPage(0).mediaBox
    upper_right = media_box.getUpperRight()
    lower_left = media_box.getLowerLeft()
    width = float(upper_right[0] - lower_left[0])
    height = float(upper_right[1] - lower_left[1])
    lines_page = get_lines_page(width, height, num_lines, horiz_margin, vert_margin, line_thickness)
    writer = PyPDF2.PdfFileWriter()
    for page_num in range(in_file.getNumPages()):
        page = in_file.getPage(page_num)
        writer.addPage(page)
        writer.addPage(lines_page)

    return writer

def main():
    parser = argparse.ArgumentParser(description=
        'Create a copy of a PDF with a page with lines on it after each page of the original PDF')
    parser.add_argument('filename', help='The filename of the input PDF')
    parser.add_argument('--numlines','-n', type=int, default=7,
                        help='The number of lines to add to each line page')
    parser.add_argument('--thickness', '-t', type=float, default=1,
                        help='The thickness of each line')
    parser.add_argument('--horizontalmargin', '-m',type=float, default=0)
    parser.add_argument('--verticalmargin', '-v',type=float, default=0)
    parser.add_argument('--outputfilename', '-o')

    args = parser.parse_args()
    if not args.outputfilename:
        args.outputfilename = re.sub(r"\.pdf$","_with_lines.pdf",args.filename)
        
    in_file = PyPDF2.PdfFileReader(args.filename)
    out_file = open(args.outputfilename,"wb")
    output_pdf = add_lines_pages(in_file,
                    args.numlines,
                    args.horizontalmargin,
                    args.verticalmargin,
                    args.thickness
                )
    output_pdf.write(out_file)

if __name__ == "__main__":
    main()



