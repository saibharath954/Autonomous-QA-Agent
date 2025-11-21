class VectorDB:
    def __init__(self):
        self.chunks = []
        self.metadata = []

    def add(self, chunk, meta):
        self.chunks.append(chunk)
        self.metadata.append(meta)

    def build(self):
        # TODO: convert chunks → embeddings → vector DB
        print("Building vector DB (placeholder)")
