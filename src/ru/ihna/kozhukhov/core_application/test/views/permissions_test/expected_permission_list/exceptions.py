class DataProviderError(Exception):
    """
    The exception will be raised when certain combination of data placed to the data provider can't
    be successfully simulated by the expected list simulator
    """

    def __init__(self):
        super().__init__("Incorrect data contained in the data provider")
