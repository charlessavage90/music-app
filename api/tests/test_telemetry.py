import json

from artistpath_api.telemetry import emit, safe_journey_id


def test_accepts_a_well_formed_journey_id():
    assert safe_journey_id("abc12345-XYZ") == "abc12345-XYZ"


def test_replaces_a_missing_journey_id():
    assert safe_journey_id(None) == "unknown"


def test_replaces_an_over_long_journey_id():
    assert safe_journey_id("a" * 65) == "unknown"


def test_replaces_a_journey_id_with_forbidden_characters():
    # A newline plus JSON punctuation is how a second log record gets injected.
    assert safe_journey_id('x"}\n{"event":"path"') == "unknown"


def test_emits_one_line_of_valid_json(capsys):
    emit({"event": "path", "journey_id": "j1", "nested": {"a": 1}})
    out = capsys.readouterr().out
    assert out.count("\n") == 1
    assert json.loads(out) == {"event": "path", "journey_id": "j1", "nested": {"a": 1}}


def test_a_value_containing_json_punctuation_is_escaped_not_injected(capsys):
    emit({"event": "path", "name": 'Bad" }\n{"event":"fake'})
    out = capsys.readouterr().out
    assert out.count("\n") == 1
    assert json.loads(out)["name"] == 'Bad" }\n{"event":"fake'
