"""Proof harness for the Friday guard in scripts/send_market_pulse.py.

Runs the real script in PULSE_MODE="send" seven times, once per weekday, with:
  - the clock pinned to 8:16 AM ET on that day,
  - urllib disabled (any network call raises), and
  - run_composio_tool replaced by a stub that records every Mailchimp call.
Expected: Mon-Thu reach the first network step and get blocked there (the guard let
them through); Fri/Sat/Sun are skipped by the guard with zero Mailchimp calls.
"""
import datetime as _dt, io, json, sys, urllib.request
from zoneinfo import ZoneInfo

SRC = open(sys.argv[1], encoding="utf-8").read()
ET = ZoneInfo("America/New_York")
# Oct 19-25, 2026 is Monday through Sunday.
days = [_dt.date(2026, 10, d) for d in range(19, 26)]

results = []
for day in days:
    class FakeDT(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return _dt.datetime(day.year, day.month, day.day, 8, 16, tzinfo=ET).astimezone(tz or ET)
    real_dt, real_open = _dt.datetime, urllib.request.urlopen
    _dt.datetime = FakeDT
    def no_network(*a, **k):
        raise RuntimeError("network disabled in test")
    urllib.request.urlopen = no_network
    calls = []
    def stub(slug, args):
        calls.append(slug)
        return {}, "stub: Mailchimp disabled in test"
    g = {"__name__": "pulse_test", "PULSE_MODE": "send", "run_composio_tool": stub}
    buf, old = io.StringIO(), sys.stdout
    sys.stdout = buf
    try:
        exec(compile(SRC, "send_market_pulse.py", "exec"), g)
    finally:
        sys.stdout = old
        _dt.datetime, urllib.request.urlopen = real_dt, real_open
    line = [l for l in buf.getvalue().splitlines() if l.startswith("PULSE_RESULT ")][0]
    out = json.loads(line[len("PULSE_RESULT "):])
    results.append((day.strftime("%A"), out["outcome"], out["reason"], len(calls)))

ok = True
for name, outcome, reason, n in results:
    expect = "skipped" if name in ("Friday", "Saturday", "Sunday") else "blocked"
    good = outcome == expect and n == 0 and (expect != "skipped" or name.split()[0] in reason or "weekend" in reason)
    ok &= good
    print(f"{'PASS' if good else 'FAIL'} {name:9s} outcome={outcome:8s} mailchimp_calls={n}  reason={reason}")
print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
