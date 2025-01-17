import fitz

# def canvas_to_pdf_points(canvas_width, canvas_height, pdf_width, pdf_height, canvas_x, canvas_y):
#     """
#     Convertir des coordonnées Canvas (pixels) en points PDF.

#     dimmension

#     Args:
#         canvas_width (float): Largeur du Canvas en pixels.
#         canvas_height (float): Hauteur du Canvas en pixels.
#         pdf_width (float): Largeur de la page PDF en points (1 point = 1/72 pouce).
#         pdf_height (float): Hauteur de la page PDF en points.
#         canvas_x (float): Coordonnée X sur le Canvas.
#         canvas_y (float): Coordonnée Y sur le Canvas.

#     Returns:
#         (float, float): Coordonnées converties en points PDF.
#     """
#     # Conversion proportionnelle
#     pdf_x = canvas_x * (pdf_width / canvas_width)*72
#     pdf_y = canvas_y * (pdf_height / canvas_height)*72
    
#     return pdf_x, pdf_y


# # Exemple d'utilisation
# canvas_width = 800  # Largeur du canvas en pixels
# canvas_height = 600  # Hauteur du canvas en pixels

# # Dimensions typiques d'une page A4 en points (1 point = 1/72 pouces)
# pdf_width = 595.2  # Largeur d'une page A4 en points
# pdf_height = 841.8  # Hauteur d'une page A4 en points

# # Coordonnées d'un point sur le canvas
# canvas_x, canvas_y = 400, 300

# # Conversion
# pdf_x, pdf_y = canvas_to_pdf_points(canvas_width, canvas_height, pdf_width, pdf_height, canvas_x, canvas_y)
# print(f"Coordonnées en points PDF : ({pdf_x}, {pdf_y})")


# Open the PDF file with fitz
pdf_document = fitz.open("bill.pdf")

        # Get the first page (assuming one-page PDF for simplicity)
page = pdf_document[0]

        # Get the dimensions of the PDF page in points (1 point = 1/72 inch)
pdf_width, pdf_height = page.rect.width, page.rect.height
