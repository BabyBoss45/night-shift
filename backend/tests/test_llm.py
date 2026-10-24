from app import llm


def test_key_is_read_from_a_local_env_file(tmp_path, monkeypatch):
    monkeypatch.delenv("MUBIT_API_KEY", raising=False)
    env = tmp_path / "keyfile"
    env.write_text("# local only\nMUBIT_API_KEY=mbt_from_file\n")
    assert llm._key(env) == "mbt_from_file"


def test_environment_variable_wins_over_the_file(tmp_path, monkeypatch):
    monkeypatch.setenv("MUBIT_API_KEY", "mbt_from_env")
    env = tmp_path / "keyfile"
    env.write_text("MUBIT_API_KEY=mbt_from_file\n")
    assert llm._key(env) == "mbt_from_env"


def test_missing_file_and_variable_mean_no_key(tmp_path, monkeypatch):
    monkeypatch.delenv("MUBIT_API_KEY", raising=False)
    assert llm._key(tmp_path / "absent") is None
