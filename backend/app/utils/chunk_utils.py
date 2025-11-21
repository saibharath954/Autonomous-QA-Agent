from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    return splitter.split_text(text)
