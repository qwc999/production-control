class BatchAlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("Batch with this number and date already exists")


class BatchNotFoundError(Exception):
    def __init__(self):
        super().__init__("Batch with this id does not exist")


class ProductAlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("Product with this code already exists")

class BatchClosedError(Exception):
    def __init__(self):
        super().__init__("Batch is closed and cannot be edited")
