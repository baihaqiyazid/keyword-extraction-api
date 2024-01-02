class ResponseFormat():
    def __init__(self, data, config, code=200, status="success", message="success"):
        self.code = code
        self.status = status
        self.message = message
        self.data = data
        self.config = config

    def to_dict(self):
        if self.data == None and self.config == None:
            return {
                "code": self.code,
                "status": self.status,
                "message": self.message,
            }
        elif self.config != None:
            return {
                "code": self.code,
                "status": self.status,
                "message": self.message,
                "config": self.config
            }
        else:
            return {
                "code": self.code,
                "status": self.status,
                "message": self.message,
                "result": self.data
            }
