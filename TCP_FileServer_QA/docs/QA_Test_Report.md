# QA Test Report — TCP File Server

- QA owner: Trần Đức Anh
- Date: _fill when running_
- Git commit / branch: _fill_
- Server build / OS / port: _fill_
- Run target: **Reference mock** initially (not real server)
- Command: `python -m unittest discover -s Code/tests -t . -v`

| ID | Test | Status (PASS/FAIL/NOT RUN) | Observed result / evidence |
| --- | --- | --- | --- |
| TC-01 | TCP connection and protocol | NOT RUN on real server | |
| TC-02 | Large file upload | NOT RUN on real server | |
| TC-03 | Concurrent uploads | NOT RUN on real server | |
| TC-04 | Abrupt disconnect | NOT RUN on real server | |
| TC-05 | Duplicate filename | NOT RUN on real server | |
| TC-06 | Invalid command | NOT RUN on real server | |

## Defects

| Bug ID | Scenario | Reproduce steps | Actual vs expected | Severity | Status |
| --- | --- | --- | --- | --- | --- |
| _fill_ | | | | | |

## Conclusion

**Not yet verified on the real application server.** Update after integration with the project protocol and capture real run evidence.
