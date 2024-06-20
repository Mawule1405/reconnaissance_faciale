import cv2
def list_cameras():
    """
    Liste les indices des caméras disponibles.
    """
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr

available_cameras = list_cameras()
print(f"Available cameras: {available_cameras}")

list_cameras()