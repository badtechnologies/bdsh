from bdsh.service.rpc import RPCSocketClient


class BadLogonClient(RPCSocketClient):
    def __init__(self):
        super().__init__("badlogon.badproc")

    def save(self):
        return self.request("save")

    def load(self):
        return self.request("load")

    def add(self, username, password):
        return self.request("add", {"username": username, "password": password})

    def get_user_by_credentials(self, username, password):
        return self.request("get_user_by_credentials", {"username": username, "password": password})

    def validate_username(self, username):
        return self.request("validate_username", username)
