class Detection:
    def __init__(self, detection_id, person_id, image_id, detection_time, confidence):
        self.detection_id = detection_id
        self.person_id = person_id
        self.image_id = image_id
        self.detection_time = detection_time
        self.confidence = confidence
