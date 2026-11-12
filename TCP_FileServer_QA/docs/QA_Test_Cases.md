# Test Cases — TCP File Server

| ID | Scenario | Steps | Expected result | Evidence |
| --- | --- | --- | --- | --- |
| TC-01 | TCP connection / protocol | Connect and send `PING` | Connection succeeds, `PONG` response | Terminal + server log |
| TC-02 | Large file (1 MiB) | Upload binary bytes | Server accepts and preserves exact file (verify checksum on real server) | Size/SHA-256 + log |
| TC-03 | Concurrent clients (10) | Run 10 simultaneous uploads with unique names | 10/10 successful, contents intact | Test result + destination list |
| TC-04 | Abrupt disconnect | Send partial upload request, close socket, then reconnect | Server stays running, accepts new requests, incomplete upload not committed | Terminal + server logs + destination |
| TC-05 | Duplicate filename | Upload `name.bin` twice with different bytes | According to project policy: reject, rename or overwrite safely; no silent corruption | Server files + error messages |
| TC-06 | Invalid protocol command | Send unknown command | Controlled error response, server does not crash | Terminal + log |

## Preconditions

- Dedicated **test server** and isolated destination storage.
- Test account permitted to create files; no actual sensitive files in target directory.
- TCP port and real protocol documented; adjust the adapter accordingly.
- TC-05 sample suite currently expects **reject with `FILE_EXISTS`**; modify if your project's actual requirement differs.

## Notes

A passing mock test proves only that the test harness works against its reference mock. Test against the **project's real server** before declaring application behavior correct.
