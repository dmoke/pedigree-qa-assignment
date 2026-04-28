class PedigreeService:
    def __init__(self, client):
        self.client = client

    def get_all(self):
        return self.client.get("/dogs")

    def get_by_id(self, dog_id: str):
        return self.client.get(f"/dogs/{dog_id}")

    def get_ancestors(self, dog_id: str):
        return self.client.get(f"/dogs/{dog_id}/ancestors")