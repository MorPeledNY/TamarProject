import cv2


def crop_image(image, x_start, y_start, width, height):
    """
    חותך את התמונה לפי הקואורדינטות שנבחרו
    :param image: התמונה המתקבלת מהמצלמה
    :param x_start: נקודת התחלה אופקית
    :param y_start: נקודת התחלה אנכית
    :param width: רוחב החיתוך
    :param height: גובה החיתוך
    :return: התמונה החתוכה
    """
    cropped_image = image[y_start:y_start + height, x_start:x_start + width]
    return cropped_image


# פתיחת המצלמה
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    # קריאה לפריים מהמצלמה
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # הגדרות לחיתוך
    x_start = 100  # התחלה בציר ה-X
    y_start = 30  # התחלה בציר ה-Y
    crop_width = 250  # רוחב החיתוך
    crop_height = 500  # גובה החיתוך

    # ביצוע חיתוך של הפריים
    cropped_frame = crop_image(frame, x_start, y_start, crop_width, crop_height)

    # הצגת הפריים המקורי והפריים החתוך
    cv2.imshow("Original Frame", frame)
    cv2.imshow("Cropped Frame", cropped_frame)

    # יציאה בלחיצה על מקש 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# שחרור המצלמה וסגירת כל החלונות
cap.release()
cv2.destroyAllWindows()
