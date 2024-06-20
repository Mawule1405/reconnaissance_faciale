class VideoSession:
    def __init__(self, session_id, start_time, end_time=None):
        self.session_id = session_id
        self.start_time = start_time
        self.end_time = end_time

    def end_session(self, end_time):
        self.end_time = end_time
