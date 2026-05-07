class BatchAlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("Batch with this number and date already exists")