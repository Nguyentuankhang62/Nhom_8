# Testing & QA — TCP File Server

**Scope:** test cases and reproducible Python `unittest` tests. No presentation slides.

> **IMPORTANT:** No actual server source/protocol was provided. By default the tests run against an **isolated reference mock** to validate the test design, **not your real application's correctness**. Adapt the protocol adapter to the actual server before calling these results final QA.

## Folder layout to copy into the project

```text
Code/
  tests/
    __init__.py
    test_tcp_qa.py
    support/
      __init__.py
      protocol_adapter.py
      mock_server.py
docs/
  QA_Test_Cases.md
  QA_Test_Report.md
README_QA.md
```

## Run

From project root (the folder containing `Code/`):

```powershell
python -m unittest discover -s Code/tests -t . -v
```

Requires Python 3.9+, standard library only. `-t .` keeps package imports working.

## Connect to your real server (after changing protocol adapter)

The sample wire format is newline-delimited UTF-8 JSON:

```json
{"command":"PING"}
{"command":"UPLOAD","filename":"qa.txt","content_b64":"aGVsbG8="}
```

Expected replies are `{"status":"OK","message":"PONG"}`, `{"status":"OK","bytes":5}` or `{"status":"ERROR","code":"FILE_EXISTS"}`. **These are assumptions, not verified project specifications.**

If your app uses binary payloads, custom commands, a handshaking step, or different error policies, edit `Code/tests/support/protocol_adapter.py` and test expectations to match the app first. Then set the real host/port:

```powershell
$env:QA_HOST = '127.0.0.1'
$env:QA_PORT = '9000'
python -m unittest discover -s Code/tests -t . -v
```

To return to mock mode:

```powershell
Remove-Item Env:QA_HOST
Remove-Item Env:QA_PORT
```

**Safety:** Run QA against a dedicated test folder/server, never production. Tests intentionally send synthetic uploaded files; network-cut test interrupts a client connection. No real network interface disruption is performed.

## Commit to Git

```powershell
git add Code/tests docs/QA_Test_Cases.md docs/QA_Test_Report.md README_QA.md
git commit -m "test: add TCP QA scenarios and unittest suite"
git push
```

## Evidence required before marking tests as passed on real server

1. Document actual server version, protocol fields, port, server configuration, and duplicate-name policy.
2. Adapt test client + expected results to that protocol.
3. Start server with isolated test storage, run all tests and capture terminal output.
4. Check resulting files on server; compare SHA-256 of 1 MiB upload and concurrent files when real app supports download or disk access.
5. Record each PASS/FAIL in `docs/QA_Test_Report.md` with screenshots/log paths and issue IDs.
