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
  "send"   the real weekday send
"""
import re, json, time, datetime, html as htmllib, urllib.request, urllib.error
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


def run():
    today = datetime.datetime.now(ET).date()

    # --- the email copy page -------------------------------------------------
    status, page = http_get(COPY_URL)
    if status != 200:
        raise Blocked("could not read the email copy page from GitHub (HTTP %s)" % status)
    copy = parse_copy(page)
    subject, preview, email_html = copy["subject_A"], copy["subject_B"], copy["member_html"]
    if not copy["date_label"] or not subject or not preview:
        raise Blocked("email copy page is missing its date, subject line A, or subject line B")
    edition = datetime.datetime.strptime(copy["date_label"], "%B %d, %Y").date()

    if MODE == "send":
        if today.weekday() > 4:
            OUT.update(outcome="skipped", reason="weekend - Market Pulse emails go out Monday to Friday")
            return
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

    # --- the newsletter page the email must open -----------------------------
    art_url = "%s/%s" % (LIVE, article_file(edition))
    status, article = http_get(art_url)
    if status != 200:
        raise Blocked("the article is not live (%s returned %s)" % (art_url, status))
    if copy["date_label"] not in article:
        raise Blocked("the live article page does not show the date " + copy["date_label"])
    passed("article is live", art_url)

    # --- every block in the email opens that page ----------------------------
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


try:
    run()
except Blocked as e:
    OUT.update(outcome="blocked", reason=str(e))
except Exception as e:  # a bug must never look like a send
    OUT.update(outcome="error", reason=repr(e)[:400])
print("PULSE_RESULT " + json.dumps(OUT))
