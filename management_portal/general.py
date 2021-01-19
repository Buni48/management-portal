class Status:
    """
    The class Status is there to check if any action was successful and which message should be sent.
    To do this you set a status bool and a message.

    Attributes:
    status  (bool): if status true
    message (str) : status message
    """
    status      = False
    message     = ''
    UNEXPECTED  = 'Es ist ein unerwarteter Fehler aufgetreten.'

    def __init__(self, status: bool = False, message: str = ''):
        self.status  = status
        self.message = message
    
    def set_unexpected(self, custom_message: str = ''):
        """
        Sets the status to false and the message to an unexpected error message.
        You can voluntarily pass a custom message.

        Parameters:
        custom_message (str): custom message to set

        Returns:
        Status: updated status
        """
        self.status = False
        if custom_message:
            self.message = custom_message
        else:
            self.message = self.UNEXPECTED

        return self


class SaveStatus(Status):
    """
    The class SaveStatus inherits from Status.
    It is there to check if the persisting was successful and which message should be sent.
    To do this you set a status bool, a message and instances need to save.

    Attributes:
    status    (bool): if status true
    message   (str) : status message
    instances (dict): dictionary of all instances to save
    """
    instances = {}

    def __init__(self, status: bool = False, message: str = '', instances: dict = {}):
        super.__init__
        self.instances = instances
