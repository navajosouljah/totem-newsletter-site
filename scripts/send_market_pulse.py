"""Totem Market Pulse -> Mailchimp sender.

Runs INSIDE the Composio remote workbench, where run_composio_tool() is preloaded.
It follows the manual routine JJ described on Oct 5 2026 (the one the Grok bot ran):

  1. duplicate the previous Market Pulse campaign
  2. paste today's MEMBER email source from email_copy.html, unchanged
  3. subject = subject line A, preview text = subject line B
  4. check that every block in the email opens today's newsletter
  5. send to the Totem LC Group list

Any failed check means nothing is sent. Re-running is safe: a campaign already sent
today is detected and skipped, and a draft left by an earlier run is reused.

The caller sets PULSE_MODE before exec():
  "check"  (default) read-only, no Mailchimp writes
  "test"   build a draft marked TEST, email it to PULSE_TEST_EMAIL only, never send
  "send"   the real Monday-to-Thursday send

Friday guard (JJ, Oct 17 2026): Claude sends the Market Pulse Monday to Thursday only.
On Fridays the Grok bot's combined Totem Challenge email carries the Market Pulse, so a
"send" on a Friday (America/New_York) exits before any Mailchimp call, whatever the
schedule that fired it says.

Sandbox without internet (Oct 2026): the Composio workbench can no longer reach the
web, but run_composio_tool() still works. So the network checks were moved into
network_checks(), which a prefetch run (scripts/prefetch_market_pulse.py, run where
there IS internet) executes to build a small bundle. Inputs:
  PULSE_PREFETCH       True only inside prefetch_market_pulse.py: define everything,
                       run nothing; the prefetch script calls build_bundle().
  PULSE_BUNDLE         dict printed by the prefetch run. When present, no http_get
                       is made: the bundle must say ok, its edition must be today
                       (send mode), and sha256(member_html) must equal both the
                       bundle's sha256 and PULSE_EXPECTED_SHA. The offline checks
                       (subjects, completeness, link rules) are re-run on it.
  PULSE_EXPECTED_SHA   the member_html sha256, copied separately by the caller.
Without PULSE_BUNDLE the script fetches everything itself, exactly as before.
"""
import re, json, time, datetime, hashlib, html as htmllib, urllib.request, urllib.error
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor

LIST_ID = "ddaa0f6b24"  # Totem LC Group audience
LIVE = "https://totem-challenge-preview.vercel.app"
EDITORIAL_HOST = "totem-editorial-review"
COPY_URL = "https://raw.githubusercontent.com/navajosouljah/totem-newsletter-site/main/email_copy.html"
ET = ZoneInfo("America/New_York")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

MODE = globals().get("PULSE_MODE", "check")
TEST_EMAIL = globals().get("PULSE_TEST_EMAIL")
PREFETCH = bool(globals().get("PULSE_PREFETCH"))
BUNDLE = globals().get("PULSE_BUNDLE")
EXPECTED_SHA = globals().get("PULSE_EXPECTED_SHA")
OUT = {"mode": MODE, "outcome": None, "reason": None, "checks": [], "warnings": []}


class Blocked(Exception):
    pass


def passed(name, detail=""):
    OUT["checks"].append(name + (": " + detail if detail else ""))


def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


def mc(slug, args):
    res, err = run_composio_tool(slug, args)
    if err:
        raise Blocked("Mailchimp step %s failed: %s" % (slug, str(err)[:300]))
    if isinstance(res, dict):
        if res.get("successful") is False or res.get("error"):
            raise Blocked("Mailchimp step %s failed: %s" % (slug, str(res.get("error"))[:300]))
        data = res.get("data", res)
        return data if isinstance(data, dict) else {}
    return {}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def template_literal(page, var):
    m = re.search(r"var\s+" + var + r"\s*=\s*`", page)
    if not m:
        raise Blocked("email copy page has no " + var)
    i, out = m.end(), []
    while True:
        ch = page[i]
        if ch == "\\":
            out.append(page[i:i + 2])
            i += 2
            continue
        if ch == "`":
            break
        out.append(ch)
        i += 1
    raw = "".join(out)
    if "${" in raw.replace("\\${", ""):
        raise Blocked("email source contains a template placeholder, not finished HTML")
    plain = {"n": "\n", "t": "\t", "r": "\r"}
    return re.sub(r"\\(.)", lambda k: plain.get(k.group(1), k.group(1)), raw, flags=re.S).strip()


def parse_copy(page):
    d = {}
    m = re.search(r"Suggested Subject Lines\s*-\s*([A-Za-z]+ \d{1,2}, \d{4})", page)
    d["date_label"] = m.group(1) if m else None
    for letter in ("A", "B"):
        m = re.search(r">" + letter + r"</span>\s*<div>\s*<p[^>]*>(.*?)</p>", page, flags=re.S)
        text = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
        d["subject_" + letter] = htmllib.unescape(text).strip()
    d["member_html"] = template_literal(page, "memberEmailHTML")
    return d


def date_label(d):
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def article_file(d):
    return "market_pulse_%s%d_%d.html" % (d.strftime("%B").lower(), d.day, d.year)


def campaign_title(d):
    return "Market Pulse Stash, %s, %s" % (d.strftime("%A"), date_label(d))


def is_pulse(c):
    t = (c.get("settings", {}).get("title") or "").lower()
    return t.startswith("market pulse") and "test" not in t


def list_campaigns(status, sort_field, count=30):
    data = mc("MAILCHIMP_LIST_CAMPAIGNS", {
        "status": status, "list_id": LIST_ID, "count": count,
        "sort_field": sort_field, "sort_dir": "DESC",
        "exclude_fields": ["campaigns._links", "_links"]})
    return data.get("campaigns") or []


def sent_on(c, day):
    st = c.get("send_time") or ""
    try:
        return datetime.datetime.fromisoformat(st).astimezone(ET).date() == day
    except ValueError:
        return False


def already_out(today, subject, ignore_id=None):
    """A Market Pulse campaign that is sent, sending, or scheduled for today."""
    hits = []
    for status in ("sent", "sending", "schedule"):
        for c in list_campaigns(status, "send_time", 15):
            if c.get("id") == ignore_id:
                continue
            same_subject = (c.get("settings", {}).get("subject_line") or "") == subject
            if same_subject or (is_pulse(c) and sent_on(c, today)):
                hits.append(c)
    return hits


SEND_DAYS = (0, 1, 2, 3)  # Monday to Thursday, America/New_York
DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def send_day_guard(today):
    """Return a skip reason when a real send must not happen today, else None.

    Runs before anything else in send mode: no email copy read, no live-page
    fetch, no Mailchimp call. Friday is blocked because the Grok bot's combined
    Totem Challenge email carries the Market Pulse (JJ, Oct 17 2026).
    """
    if today.weekday() in SEND_DAYS:
        return None
    if today.weekday() == 4:
        return ("Friday - Claude does not send the Market Pulse on Fridays; "
                "the Totem Challenge email (Grok bot) carries it. Nothing was sent.")
    return "weekend - Market Pulse emails go out Monday to Thursday. Nothing was sent."


def today_et():
    return datetime.datetime.now(ET).date()


def test_ignore_send_day():
    """Test-only: skip the weekday guard. Honoured only when run_composio_tool is the
    box test mock (it carries __pulse_mock__), so it can never affect a real run."""
    tool = globals().get("run_composio_tool")
    return bool(globals().get("PULSE_TEST_IGNORE_SEND_DAY")) and bool(getattr(tool, "__pulse_mock__", False))


def check_copy(copy, today):
    """No-network checks on the parsed email copy. Returns the edition date."""
    subject, preview, email_html = copy["subject_A"], copy["subject_B"], copy["member_html"]
    if not copy["date_label"] or not subject or not preview:
        raise Blocked("email copy page is missing its date, subject line A, or subject line B")
    edition = datetime.datetime.strptime(copy["date_label"], "%B %d, %Y").date()

    if MODE == "send":
        if edition != today:
            raise Blocked("the email copy page is dated %s, not today (%s) - today's Market Pulse has not landed"
                          % (copy["date_label"], date_label(today)))
    elif edition != today:
        OUT["warnings"].append("email copy page is dated %s, today is %s" % (copy["date_label"], date_label(today)))
    passed("email copy page read", "edition " + copy["date_label"])

    for name, text in (("subject line A", subject), ("subject line B", preview)):
        if not 10 <= len(text) <= 150 or "<" in text:
            raise Blocked("%s looks wrong: %r" % (name, text[:160]))
    low = email_html.lower()
    if not (low.startswith("<!doctype") and low.rstrip().endswith("</html>")
            and 6000 <= len(email_html) <= 80000 and "totem lc group" in low):
        raise Blocked("the member email source is not a complete Totem email (%d characters)" % len(email_html))
    passed("member email source is complete", "%d characters" % len(email_html))
    return edition


def link_rules(email_html, art_url):
    """No-network href rules. Returns (web links, links to today's article)."""
    hrefs = [htmllib.unescape(h) for h in re.findall(r'href\s*=\s*"([^"]+)"', email_html)]
    web = [h for h in dict.fromkeys(hrefs) if h.lower().startswith(("http://", "https://"))]
    base = lambda h: h.split("#")[0].split("?")[0]
    to_article = [h for h in web if base(h) == art_url]
    if not to_article:
        raise Blocked("no link in the email opens today's article")
    if any(EDITORIAL_HOST in h for h in web):
        raise Blocked("the email links to the editorial review site")
    other_day = [h for h in web if re.search(r"/market_pulse_[a-z]+\d+_\d{4}\.html", h) and base(h) != art_url]
    if other_day:
        raise Blocked("the email links to a different day's Market Pulse: " + ", ".join(other_day[:3]))
    return web, to_article


def network_checks(today):
    """Every step that needs the internet. Returns (copy, edition)."""
    # --- the email copy page -------------------------------------------------
    status, page = http_get(COPY_URL)
    if status != 200:
        raise Blocked("could not read the email copy page from GitHub (HTTP %s)" % status)
    copy = parse_copy(page)
    edition = check_copy(copy, today)

    # --- the newsletter page the email must open -----------------------------
    art_url = "%s/%s" % (LIVE, article_file(edition))
    status, article = http_get(art_url)
    if status != 200:
        raise Blocked("the article is not live (%s returned %s)" % (art_url, status))
    if copy["date_label"] not in article:
        raise Blocked("the live article page does not show the date " + copy["date_label"])
    passed("article is live", art_url)

    # --- every block in the email opens that page ----------------------------
    web, to_article = link_rules(copy["member_html"], art_url)
    for h in to_article:
        frag = h.split("#", 1)[1] if "#" in h else ""
        if frag and not re.search(r"id\s*=\s*[\"']%s[\"']" % re.escape(frag), article):
            raise Blocked("an email block points at #%s, which is not on today's page" % frag)
    pages = list(dict.fromkeys(h.split("#")[0] for h in web))
    with ThreadPoolExecutor(8) as pool:
        codes = list(pool.map(lambda u: (u, http_get(u)[0]), pages))
    dead = [u for u, code in codes if code != 200]
    if any(u.startswith(LIVE) for u in dead):
        raise Blocked("a link in the email does not open: " + ", ".join(u for u in dead if u.startswith(LIVE)))
    for u in dead:
        OUT["warnings"].append("outside link did not answer 200: " + u)
    passed("every block opens today's newsletter",
           "%d links, %d to today's article" % (len(web), len(to_article)))
    return copy, edition


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_bundle():
    """Prefetch: run network_checks() and return the small bundle the workbench needs.
    Never touches Mailchimp."""
    today = today_et()
    b = {"bundle_version": 1, "mode": MODE, "made_at": datetime.datetime.now(ET).isoformat(timespec="seconds"),
         "outcome": None, "reason": None}
    try:
        if MODE == "send" and not test_ignore_send_day():
            reason = send_day_guard(today)
            if reason:
                b.update(outcome="skipped", reason=reason, checks=[], warnings=[])
                return b
        copy, edition = network_checks(today)
        b.update(date_label=copy["date_label"], edition=edition.isoformat(),
                 subject_A=copy["subject_A"], subject_B=copy["subject_B"],
                 member_html=copy["member_html"], sha256=sha256_text(copy["member_html"]),
                 outcome="ok")
    except Blocked as e:
        b.update(outcome="blocked", reason=str(e))
    except Exception as e:
        b.update(outcome="blocked", reason="prefetch error: " + repr(e)[:400])
    b.update(checks=OUT["checks"], warnings=OUT["warnings"])
    return b


def bundle_checks(today):
    """Workbench path: verify the prefetch bundle instead of fetching. Returns (copy, edition)."""
    b = BUNDLE
    if not isinstance(b, dict):
        raise Blocked("PULSE_BUNDLE is not a dict")
    if b.get("outcome") != "ok":
        raise Blocked("the prefetch bundle is not ok (%s): %s" % (b.get("outcome"), b.get("reason")))
    if MODE == "send" and b.get("mode") != "send":
        raise Blocked("the prefetch bundle was made in %r mode, not send" % b.get("mode"))
    copy = {k: b.get(k) for k in ("date_label", "subject_A", "subject_B", "member_html")}
    if not all(isinstance(copy[k], str) for k in copy):
        raise Blocked("the prefetch bundle is missing the date, subjects, or member email")
    got = sha256_text(copy["member_html"])
    if got != b.get("sha256"):
        raise Blocked("member email sha256 %s does not match the bundle's %s - the bundle was altered or mis-copied"
                      % (got, str(b.get("sha256"))[:64]))
    if not EXPECTED_SHA or got != str(EXPECTED_SHA).strip().lower():
        raise Blocked("member email sha256 %s does not match PULSE_EXPECTED_SHA %s"
                      % (got, str(EXPECTED_SHA)[:64]))
    passed("prefetch bundle verified", "sha256 %s, made %s" % (got[:12], b.get("made_at")))
    edition = check_copy(copy, today)
    if b.get("edition") != edition.isoformat():
        raise Blocked("the bundle edition %s does not match its date label %s" % (b.get("edition"), copy["date_label"]))
    art_url = "%s/%s" % (LIVE, article_file(edition))
    web, to_article = link_rules(copy["member_html"], art_url)
    passed("link rules re-checked offline", "%d links, %d to today's article" % (len(web), len(to_article)))
    for c in b.get("checks") or []:
        passed("prefetch: " + c)
    for w in b.get("warnings") or []:
        OUT["warnings"].append("prefetch: " + w)
    return copy, edition


def run():
    today = today_et()

    if MODE == "send" and not test_ignore_send_day():
        reason = send_day_guard(today)
        if reason:
            OUT.update(outcome="skipped", reason=reason, day=DAY_NAMES[today.weekday()])
            return

    if BUNDLE is not None:
        OUT["path"] = "bundle"
        copy, edition = bundle_checks(today)
    else:
        OUT["path"] = "network"
        copy, edition = network_checks(today)
    subject, preview, email_html = copy["subject_A"], copy["subject_B"], copy["member_html"]

    # --- Mailchimp: nothing already out, and a campaign to duplicate ---------
    if MODE == "send":
        out_already = already_out(today, subject)
        if out_already:
            OUT.update(outcome="skipped",
                       reason="today's Market Pulse already went out: " + (out_already[0]["settings"].get("title") or ""))
            return
    sent = [c for c in list_campaigns("sent", "send_time", 25) if is_pulse(c)]
    if not sent:
        raise Blocked("no earlier Market Pulse campaign found to duplicate")
    source = sent[0]
    if source.get("recipients", {}).get("list_id") != LIST_ID or not source.get("emails_sent"):
        raise Blocked("the previous Market Pulse campaign is not on the Totem LC Group list")
    passed("previous campaign found", source["settings"].get("title") or source["id"])

    title = campaign_title(edition)
    if MODE != "send":
        title = "TEST - safe to delete - " + title
    OUT.update(subject=subject, preview=preview, title=title, duplicated_from=source["settings"].get("title"))
    if MODE == "check":
        OUT.update(outcome="checked", reason="all checks passed, nothing written to Mailchimp")
        return

    # --- duplicate, paste, subject A, preview B ------------------------------
    drafts = [c for c in list_campaigns("save", "create_time", 30) if c.get("settings", {}).get("title") == title]
    if drafts:
        cid = drafts[0]["id"]
    else:
        cid = mc("MAILCHIMP_REPLICATE_CAMPAIGN", {"campaign_id": source["id"]}).get("id")
    if not cid:
        raise Blocked("Mailchimp did not return a duplicated campaign")
    OUT["campaign_id"] = cid
    mc("MAILCHIMP_UPDATE_CAMPAIGN_SETTINGS", {
        "campaign_id": cid, "settings__title": title,
        "settings__subject__line": subject, "settings__preview__text": preview,
        "settings__from__name": source["settings"].get("from_name"),
        "settings__reply__to": source["settings"].get("reply_to")})
    mc("MAILCHIMP_SET_CAMPAIGN_CONTENT", {"campaign_id": cid, "html": email_html})

    # --- read it back before trusting it -------------------------------------
    info = mc("MAILCHIMP_GET_CAMPAIGN_INFO", {"campaign_id": cid, "exclude_fields": ["_links"]})
    st, rc = info.get("settings", {}), info.get("recipients", {})
    if info.get("status") != "save":
        raise Blocked("the new campaign is not a draft (status %s)" % info.get("status"))
    if rc.get("list_id") != LIST_ID or (rc.get("segment_text") or "").strip():
        raise Blocked("the new campaign is not addressed to the whole Totem LC Group list")
    if st.get("subject_line") != subject or st.get("preview_text") != preview or st.get("title") != title:
        raise Blocked("Mailchimp did not save the subject, preview, or name as set")
    count, before = rc.get("recipient_count") or 0, source["emails_sent"]
    if count <= 0 or abs(count - before) > max(5, 0.2 * before):
        raise Blocked("recipient count is %s, the last send went to %s" % (count, before))
    stored = mc("MAILCHIMP_GET_CAMPAIGN_CONTENT", {"campaign_id": cid}).get("html") or ""
    if norm(email_html[:email_html.rfind("</body>")]) not in norm(stored):
        raise Blocked("Mailchimp did not store the email exactly as pasted")
    checklist = mc("MAILCHIMP_GET_CAMPAIGN_SEND_CHECKLIST", {"campaign_id": cid, "exclude_fields": ["_links"]})
    errors = [i.get("heading") or i.get("details") or "" for i in checklist.get("items") or [] if i.get("type") == "error"]
    if errors or checklist.get("is_ready") is False:
        raise Blocked("Mailchimp's send checklist is not clear: " + "; ".join(errors)[:300])
    OUT["recipients"] = count
    passed("draft built and read back", "%d recipients, subject and preview match, content matches" % count)

    if MODE == "test":
        if not TEST_EMAIL:
            raise Blocked("no test address given")
        mc("MAILCHIMP_SEND_TEST_EMAIL", {"campaign_id": cid, "test_emails": [TEST_EMAIL], "send_type": "html"})
        OUT.update(outcome="test_sent", reason="test email sent to the test address only; the draft was not sent")
        return

    # --- send ----------------------------------------------------------------
    raced = already_out(today, subject, ignore_id=cid)
    if raced:
        OUT.update(outcome="skipped",
                   reason="another Market Pulse went out while this one was being built; the draft was left unsent")
        return
    send_error = ""
    try:
        mc("MAILCHIMP_SEND_CAMPAIGN", {"campaign_id": cid})
    except Blocked as e:
        send_error = str(e)
    state = ""
    for _ in range(8):
        time.sleep(5)
        state = mc("MAILCHIMP_GET_CAMPAIGN_INFO", {"campaign_id": cid, "exclude_fields": ["_links"]}).get("status") or ""
        if state in ("sending", "sent"):
            break
    if state not in ("sending", "sent"):
        raise Blocked("the send did not start (status %s) %s" % (state, send_error))
    OUT.update(outcome="sent", reason="sent to %d members" % count, status=state)


if not PREFETCH:
    try:
        run()
    except Blocked as e:
        OUT.update(outcome="blocked", reason=str(e))
    except Exception as e:  # a bug must never look like a send
        OUT.update(outcome="error", reason=repr(e)[:400])
    print("PULSE_RESULT " + json.dumps(OUT))
