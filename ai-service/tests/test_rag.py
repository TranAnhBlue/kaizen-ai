from app.modules.chatbot.rag_service import chunk_text, extract_text

def test_chunk_overlap():
    data = 'a' * 2000
    chunks = chunk_text(data)
    assert len(chunks) == 3
    assert chunks[0][-120:] == chunks[1][:120]

def test_plain_text():
    assert extract_text(b'Kaizen', 'text/plain') == 'Kaizen'
