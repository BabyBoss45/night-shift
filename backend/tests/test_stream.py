import json
import threading
import time
from itertools import pairwise

import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app
from app.pipeline import T1Result

TEXT = ("Tenant: Raj Patel, sort code 20-45-77.\n\n" + "Clause text. " * 30 + "\n\n"
        + "Landlord: Jo Smith.\n\n" + "More clause text. " * 30 + "\n\nSigned: Raj Patel")


def parse(body: str) -> tuple[list[tuple[str, dict]], int]:
    """(events as (name, data), number of ping comments) from a text/event-stream body."""
    events, pings = [], 0
    for block in body.split("\n\n"):
        if not block:
            continue
        if block == ": ping":
            pings += 1
            continue
        name_line, data_line = block.split("\n")
        assert name_line.startswith("event: ") and data_line.startswith("data: ")
        events.append((name_line[7:], json.loads(data_line[6:])))
    return events, pings


def finds(*values):
    def factory(doc_id):
        def t1(chunk):
            return T1Result([{"text": v, "type": "PERSON"} for v in values if v in chunk], f"mreq_{doc_id}", None)
        return t1
    return factory


@pytest.fixture
def setup(monkeypatch):
    """A client, and a way to swap the T1 factory and the chunk size (the evalkit default is 4000)."""
    monkeypatch.setitem(main.T1_CHUNK_CHARS, "evalkit", 400)
    monkeypatch.setattr(app.state, "t1_prompt", "evalkit")
    monkeypatch.setattr(app.state, "t1_model", "gpt-6-luna")

    def with_t1(factory):
        monkeypatch.setattr(app.state, "t1_factory", factory)
        return TestClient(app)
    return with_t1


def stream(client, text=TEXT):
    doc = client.post("/api/documents", data={"text": text}).json()
    res = client.post(f"/api/documents/{doc['doc_id']}/redact/stream")
    assert res.status_code == 200
    return doc, res


def test_events_come_in_order_with_the_contract_headers(setup):
    doc, res = stream(setup(finds("Raj Patel", "Jo Smith")))
    assert res.headers["content-type"] == "text/event-stream"
    assert res.headers["cache-control"] == "no-cache" and res.headers["x-accel-buffering"] == "no"
    events, _ = parse(res.text)
    names = [n for n, _ in events]
    n_chunks = len(events[0][1]["chunks"])
    assert n_chunks > 1
    assert names == ["start", "regex"] + ["chunk"] * n_chunks + ["done"]
    start = events[0][1]
    assert list(start) == ["doc_id", "model", "t1_model", "t1_prompt", "chunks"]
    assert (start["doc_id"], start["model"], start["t1_model"], start["t1_prompt"]) == (
        doc["doc_id"], "on", "gpt-6-luna", "evalkit")


def test_start_lists_every_chunk_and_they_cover_the_text(setup):
    doc, res = stream(setup(finds()))
    chunks = parse(res.text)[0][0][1]["chunks"]
    assert [c["index"] for c in chunks] == list(range(len(chunks)))
    assert [c["chunk_id"] for c in chunks] == [f"{doc['doc_id']}-c{i:02d}" for i in range(len(chunks))]
    assert chunks[0]["start"] == 0 and chunks[-1]["end"] == len(doc["text"])
    assert all(a["end"] == b["start"] for a, b in pairwise(chunks))
    assert all(set(c) == {"index", "chunk_id", "start", "end"} for c in chunks)


def test_chunk_entities_stay_inside_their_range(setup):
    doc, res = stream(setup(finds("Raj Patel", "Jo Smith")))
    events, _ = parse(res.text)
    chunk_events = [d for n, d in events if n == "chunk"]
    assert sum(len(c["entities"]) for c in chunk_events) == 3  # Raj Patel twice, Jo Smith once
    for c in chunk_events:
        assert set(c) == {"index", "chunk_id", "start", "end", "status", "error", "mreq_id", "latency_ms",
                          "found", "entities"}
        assert c["status"] == "ok" and c["mreq_id"] == f"mreq_{doc['doc_id']}" and isinstance(c["latency_ms"], int)
        assert c["found"] == len({e["text"] for e in c["entities"]})
        for e in c["entities"]:
            assert c["start"] <= e["start"] < e["end"] <= c["end"]
            assert doc["text"][e["start"]:e["end"]] == e["text"] and e["source"] == "model"
    regex = events[1][1]["entities"]
    assert regex == [{"start": 29, "end": 37, "text": "20-45-77", "type": "SORT_CODE", "source": "regex"}]


def test_done_is_the_redact_result_and_the_result_is_stored(setup):
    client = setup(finds("Raj Patel", "Jo Smith"))
    doc, res = stream(client)
    done = parse(res.text)[0][-1][1]
    did = doc["doc_id"]
    assert done == main._result_payload(main.DOCS[did], main.RESULTS[did])
    assert [c["index"] for c in done["chunks"]] == list(range(len(done["chunks"])))
    again = client.post(f"/api/documents/{did}/redact").json()
    def no_latency(r):
        return {**r, "chunks": [{**c, "latency_ms": None} for c in r["chunks"]]}
    assert no_latency(done) == no_latency(again)
    # /file and /corrections work straight after the stream
    assert "Raj Patel" not in client.get(f"/api/documents/{did}/file").text
    fixed = client.post(f"/api/documents/{did}/corrections", json={"action": "unhide", "text": "Jo Smith"}).json()
    assert "Landlord: Jo Smith." in fixed["redacted_text"]


def test_unknown_document_is_404_before_any_stream(setup):
    res = setup(finds()).post("/api/documents/nope/redact/stream")
    assert res.status_code == 404 and res.json() == {"detail": "Document not found. Upload it again."}


def test_model_off_marks_every_chunk_off_and_regex_still_works(setup):
    _, res = stream(setup(None))
    events, _ = parse(res.text)
    start, chunk_events, done = events[0][1], [d for n, d in events if n == "chunk"], events[-1][1]
    assert (start["model"], start["t1_model"], start["t1_prompt"]) == ("off", None, "evalkit")
    assert chunk_events and all(c["status"] == "off" and c["entities"] == [] and c["mreq_id"] is None
                                for c in chunk_events)
    assert [e["text"] for e in events[1][1]["entities"]] == ["20-45-77"]
    assert done["model"] == "off" and "[SORT_CODE_1]" in done["redacted_text"]


def test_a_chunk_that_raises_is_an_error_chunk_and_the_run_finishes(setup):
    def factory(doc_id):
        def t1(chunk):
            if "Landlord" in chunk:
                raise ConnectionError("gateway went away")
            return T1Result([{"text": "Raj Patel", "type": "PERSON"}] if "Raj Patel" in chunk else [], "mreq_ok", None)
        return t1

    _, res = stream(setup(factory))
    events, _ = parse(res.text)
    assert events[-1][0] == "done" and "error" not in [n for n, _ in events]
    bad = [d for n, d in events if n == "chunk" and d["status"] == "error"]
    assert len(bad) == 1 and bad[0]["error"] == "ConnectionError: gateway went away" and bad[0]["entities"] == []
    assert "[PERSON_1]" in events[-1][1]["redacted_text"]


def test_an_empty_chunk_is_not_sent(setup):
    calls = []

    def factory(doc_id):
        def t1(chunk):
            calls.append(chunk)
            return T1Result([], None, None)
        return t1

    _, res = stream(setup(factory), "Hello there.\n\n" + " " * 400)  # two chunks of at most 400
    statuses = [d["status"] for n, d in parse(res.text)[0] if n == "chunk"]
    assert sorted(statuses) == ["empty", "ok"] and calls == ["Hello there.\n\n"]


def test_chunks_arrive_in_the_order_they_finish(setup):
    second_done = threading.Event()

    def factory(doc_id):
        def t1(chunk):
            if "Tenant" in chunk:
                second_done.wait(5)  # the first chunk finishes last, well after the second
                time.sleep(0.3)
            else:
                second_done.set()
            return T1Result([], None, None)
        return t1

    _, res = stream(setup(factory), "Tenant here.\n\n" + "x " * 200)  # two chunks of at most 400
    order = [d["index"] for n, d in parse(res.text)[0] if n == "chunk"]
    assert order == [1, 0]


def test_pings_keep_a_slow_stream_open(setup, monkeypatch):
    monkeypatch.setattr(main, "PING_SECONDS", 0.05)

    def factory(doc_id):
        def t1(chunk):
            time.sleep(0.3)
            return T1Result([], None, None)
        return t1

    _, res = stream(setup(factory), "Short text.")
    events, pings = parse(res.text)
    assert pings >= 2 and [n for n, _ in events] == ["start", "regex", "chunk", "done"]


def test_an_unexpected_failure_sends_an_error_event_and_ends(setup, monkeypatch):
    def broken(doc, t1, max_chars, emit):
        emit("start", {"chunks": []})
        raise KeyError("Raj Patel")

    monkeypatch.setattr(main, "run_pipeline", broken)
    _, res = stream(setup(finds()))
    events, _ = parse(res.text)
    assert [n for n, _ in events] == ["start", "error"]
    assert "Raj Patel" not in events[-1][1]["message"] and events[-1][1]["message"]


def test_rewrite_prompt_uses_short_chunks(setup, monkeypatch):
    monkeypatch.setattr(app.state, "t1_prompt", "rewrite")
    monkeypatch.setattr(app.state, "t1_model", "claude-haiku-4-5")
    monkeypatch.setitem(main.T1_CHUNK_CHARS, "rewrite", 1400)
    _, res = stream(setup(finds()), "word " * 1000)
    start = parse(res.text)[0][0][1]
    assert start["t1_prompt"] == "rewrite" and start["t1_model"] == "claude-haiku-4-5"
    assert len(start["chunks"]) == 4 and all(c["end"] - c["start"] <= 1400 for c in start["chunks"])


def test_logs_hold_metadata_only(setup, caplog):
    caplog.set_level("INFO", logger="veil")
    doc, _ = stream(setup(finds("Raj Patel", "Jo Smith")))
    assert f"doc={doc['doc_id']}" in caplog.text and "status=ok" in caplog.text and "found=" in caplog.text
    for secret in ("Raj Patel", "Jo Smith", "20-45-77", "Clause text"):
        assert secret not in caplog.text
