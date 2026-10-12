import pytest
from tripcost.jsliteral import JsLiteralError, literal_after

SOURCE = """
/** The dataset */
const TOLL_DATA = [
  // a frontal plaza
  {
    id: "a1_afidnes", name_gr: 'Διόδια Αφιδνών',
    lat: 38.17, lng: -23.85, cat2: 3.90,  /* car */
    isNew: true, status: null, via: [{ lat: 1, lng: 2, }, ],
    note: "say \\"hi\\"\\u0021",
  },
];
function helper() { return 1; }
"""


def test_reads_the_data_after_the_marker():
    stations = literal_after(SOURCE, "const TOLL_DATA =")
    assert stations == [{"id": "a1_afidnes", "name_gr": "Διόδια Αφιδνών", "lat": 38.17, "lng": -23.85,
                         "cat2": 3.9, "isNew": True, "status": None, "via": [{"lat": 1, "lng": 2}],
                         "note": 'say "hi"!'}]


def test_refuses_code():
    with pytest.raises(JsLiteralError):
        literal_after("const TOLL_DATA = [fetch('x')];", "const TOLL_DATA =")


def test_refuses_a_missing_marker():
    with pytest.raises(JsLiteralError):
        literal_after("const OTHER = [];", "const TOLL_DATA =")
