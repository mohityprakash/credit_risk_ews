from app.utils.hashing import hash_url


def test_hash_url_is_stable():
    url = "https://example.com/item"
    assert hash_url(url) == hash_url(url)


def test_hash_url_trims_whitespace():
    assert hash_url(" https://example.com/item ") == hash_url("https://example.com/item")
