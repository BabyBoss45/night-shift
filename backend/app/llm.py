"""The two model calls, both through Mubit.

T1 finds personal data in a chunk. It uses the frozen prompt from evalkit, with recording left on so
the calls keep training the adapter. T2 answers a question about the redacted text. It is sent with
`x-middleware-record: off`, so it creates no second task and Mubit stores no user questions.
The key comes from MUBIT_API_KEY or from a line `MUBIT_API_KEY=mbt_...` in backend/.env.
Without a key both are off and the app runs on the regex layer only.
"""

import os
from collections.abc import Callable
from pathlib import Path

from evalkit import providers
from evalkit.prompts import T1_SYSTEM_PROMPT
from evalkit.send_batch import parse_entities

from .pipeline import T1Result

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"  # backend/.env, gitignored; the shell variable wins
T1_MODEL = os.environ.get("VEIL_T1_MODEL", "gpt-6-luna")
T2_MODEL = os.environ.get("VEIL_T2_MODEL", "claude-haiku-4-5")

T2_SYSTEM_PROMPT = (
    "Answer the user's question about a redacted document. Values in square brackets such as "
    "[PERSON_1] or [ACCOUNT_2] stand for hidden real values. Keep every placeholder exactly as "
    "written. Never guess hidden values. Answer briefly and plainly."
)


def _key(env_file: Path = ENV_FILE) -> str | None:
    key = os.environ.get("MUBIT_API_KEY")
    if not key and env_file.is_file():
        for line in env_file.read_text().splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "MUBIT_API_KEY":
                key = value.strip().strip("'\"")
    return key if key and key.startswith("mbt_") else None


def make_t1_factory() -> Callable[[str], Callable[[str], T1Result]] | None:
    key = _key()
    if not key:
        return None
    call = providers.CALL[providers.provider_for(T1_MODEL)]

    def factory(doc_id: str) -> Callable[[str], T1Result]:
        def t1(chunk: str) -> T1Result:
            rep = call(key, T1_MODEL, T1_SYSTEM_PROMPT, chunk, f"doc-{doc_id}", {}, True, 8000)
            if rep.status != 200 or rep.text is None:
                return T1Result([], rep.mreq_id, rep.stop_reason)
            if rep.stop_reason in ("length", "max_tokens", "MAX_TOKENS"):
                return T1Result([], rep.mreq_id, "answer cut off")
            ents, bad = parse_entities(rep.text)
            return T1Result(ents, rep.mreq_id, "unreadable answer" if bad else None)
        return t1

    return factory


def make_t2() -> Callable[[str, str], tuple[str, str | None]] | None:
    key = _key()
    if not key:
        return None
    call = providers.CALL[providers.provider_for(T2_MODEL)]

    def t2(question: str, redacted_text: str) -> tuple[str, str | None]:
        user = f"Document:\n{redacted_text}\n\nQuestion: {question}"
        rep = call(key, T2_MODEL, T2_SYSTEM_PROMPT, user, "veil-chat", {"x-middleware-record": "off"}, False, 2000)
        if rep.status != 200 or rep.text is None:
            raise RuntimeError(rep.stop_reason or "no answer")
        return rep.text, rep.mreq_id

    return t2
