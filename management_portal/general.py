class Status:
    """
    The class Status is there to check if any action was successful and which message should be sent.
    To do this you set a status bool and a message.

    Attributes:
    status  (bool): if status true
    message (str) : status message
    """
    status  = False
    message = ''

    def __init__(self, status: bool = False, message: str = ''):
        self.status  = status
        self.message = message
