"""Totem Market Pulse prefetch - runs where there IS internet (Claude's own bash).

The Composio workbench lost outbound internet in Oct 2026, so this script does every
network step of send_market_pulse.py (email copy page, parse, date / subject /
completeness checks, article live with its date, every href rule, #fragments on the
article page, 200 check on every linked page) by loading the sender itself in
prefetch mode and calling its build_bundle(). No check is copied here; they all live
in the sender. Nothing here touches Mailchimp.

Usage:  python3 prefetch_market_pulse.py [send|check|test] [--sender PATH]
        (default mode send; default sender = send_market_pulse.py next to this file)

Output (stdout):
  PULSE_BUNDLE {...compact JSON...}      one line, pure ASCII, contains no ' character
  PULSE_SHA <sha256 of member_html>      only when outcome is ok
The bundle outcome is ok, blocked (with reason) or skipped (send-day guard).
Python 3.9+, standard library only.
"""
import hashlib, json, os, sys

# sha256 of the send_market_pulse.py this prefetch was released with. The sender is
# refused if it differs, so pinning this file's hash pins both scripts.
SENDER_SHA256 = "4ef4d4ed78a5b2ac4d85882420dd3c15b361642833ae5c39bdd1ce325ae12d96"


def emit(bundle):
    text = json.dumps(bundle, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    text = text.replace("'", "\\u0027")  # safe inside a Python r'''...''' literal
    print("PULSE_BUNDLE " + text)
    if bundle.get("outcome") == "ok":
        print("PULSE_SHA " + bundle["sha256"])


def main(argv):
    mode, sender = "send", os.path.join(os.path.dirname(os.path.abspath(__file__)), "send_market_pulse.py")
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--sender" and args:
            sender = args.pop(0)
        elif a in ("send", "check", "test"):
            mode = a
        else:
            emit({"bundle_version": 1, "mode": mode, "outcome": "blocked", "reason": "unknown argument %r" % a})
            return 0
    try:
        with open(sender, "rb") as f:
            raw = f.read()
    except OSError as e:
        emit({"bundle_version": 1, "mode": mode, "outcome": "blocked", "reason": "sender not readable: %s" % e})
        return 0
    got = hashlib.sha256(raw).hexdigest()
    if got != SENDER_SHA256:
        emit({"bundle_version": 1, "mode": mode, "outcome": "blocked",
              "reason": "send_market_pulse.py sha256 %s is not the pinned %s" % (got, SENDER_SHA256)})
        return 0
    g = {"__name__": "pulse_prefetch", "PULSE_MODE": mode, "PULSE_PREFETCH": True}
    exec(compile(raw.decode("utf-8"), sender, "exec"), g)
    bundle = g["build_bundle"]()
    bundle["sender_sha256"] = got
    emit(bundle)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
