from app.utils.json_parser import safe_parse_model_output


def test_safe_parse_model_output_json():
    raw = '{"summary":"ok","risk_score":45}'
    parsed = safe_parse_model_output(raw)
    assert parsed["summary"] == "ok"


def test_safe_parse_model_output_markdown_fence():
    raw = '```json\n{"summary":"ok","risk_score":45}\n```'
    parsed = safe_parse_model_output(raw)
    assert parsed["risk_score"] == 45
