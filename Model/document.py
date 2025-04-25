class Document:
    def __init__(self, text, metadata=None):
        self.text = text
        self.metadata = metadata or {}

    def get_text(self):
        return self.text

    def get_metadata(self):
        return self.metadata
