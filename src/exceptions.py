class QuotaExceededException(Exception):
    def __init__(self):
        super().__init__()
        
class ConfirmationNeededException(Exception):
    def __init__(self):
        super().__init__()

class NoImageDataException(Exception):
    def __init__(self):
        super().__init__()
