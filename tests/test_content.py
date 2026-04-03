from app.services.ai_service import AIService


def test_content_hash_stable():
    text = 'hello world'
    h1 = AIService.content_hash(text)
    h2 = AIService.content_hash(text)
    assert h1 == h2
    assert len(h1) == 64
