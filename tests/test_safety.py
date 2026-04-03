from app.services.safety_service import detect_red_flags, medical_disclaimer


def test_red_flags_detected():
    flags = detect_red_flags('I have chest pain and shortness of breath')
    assert 'chest pain' in flags
    assert 'shortness of breath' in flags


def test_disclaimer_english():
    assert 'educational' in medical_disclaimer('en')
