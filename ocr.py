from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    filename = "{}.png".format("temp")
    cv2.imwrite(filename, gray)
    text = pytesseract.image_to_string(Image.open(filename))
    return text