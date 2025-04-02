class RequestSingleton:
    _instance = None

    def __new__(cls):
        """Ensures only one instance of RequestSingleton exists.

        Returns:
            RequestSingleton: The singleton instance.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.request = None
        return cls._instance
