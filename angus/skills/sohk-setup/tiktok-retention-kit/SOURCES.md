# Sources and verification — 30 October 2026

## Original source and changes

Derived from the `pull.js` page-response listener and parser in TikTok Sync, downloaded for inspection from:
https://res.cloudinary.com/dailcoaeb/raw/upload/vault/lead-magnets/content-agent-setup-prompts/tiktok-sync.zip

The derivative is deliberately named Interview clip retention kit. It does not claim to be the unchanged source. The signed-in Studio read remains the same basic mechanism. It collects only the explicitly identified clips in a reader-owned local JSON file. It omits the full-archive catalog, database, scheduled refresh logic, diagnostic traffic recorder, cookie resets and optional replay requests. It preserves fractional timestamps, validates the curve, checks requested post IDs and payload IDs where present, and adds exact clip-to-source mapping. No Angus paths, account IDs, credentials or database names are required.

TikTok Studio's internal page response used by this helper is not a stable documented public API. The source listener recognizes `/aweme/v2/data/insight/` with `video_retention_rate_realtime.value.list`, each entry containing `timestamp` in milliseconds and `value` as the retained fraction. A changed shape is reported unavailable until verified and adapted; it is never silently converted to zeros.

## Official current documentation fetched this run

- TikTok Studio help: https://support.tiktok.com/en/using-tiktok/creating-videos/creator-tools-on-tiktok . Web entry is www.tiktok.com/tiktokstudio. The documented navigation is Analytics and Content for individual video metrics. App route: Profile → Menu → TikTok Studio, and individual posts offer More insights. Availability varies across app/web and region. Existing real UI capture inspected in the source project shows Overview → Retention rate, with the message “Most viewers stopped watching at 0:01” for that example post. This kit navigates directly to the exact post's analytics URL, so it does not require a fragile sequence of sidebar clicks.
- TikTok Accounts API: https://business-api.tiktok.com/portal/docs/get-post-data-of-a-tiktok-account/v1.3 . GET `https://business-api.tiktok.com/open_api/v1.3/business/video/list/`, creator-authorized `Access-Token` header, required `business_id` (OAuth `open_id`), requested `fields` including `item_id`. `video_view_retention` returns `{second,percentage}` under `video.insights`; response is paginated. Accounts API access application review is required for new apps or scope increases. Several metrics have a 24–48-hour delay. This is an option for a reader who already has approved access, not something the kit secretly depends on. Do not claim that TikTok has no official retention API.
- Playwright installation and supported Node/OS versions: https://playwright.dev/docs/intro . The current page lists latest Node 22.x, 24.x or 26.x; macOS 14+, Windows 11+/Server 2019+/WSL, supported Debian/Ubuntu releases. Package locks Playwright 1.61.1.
- Node installer: https://nodejs.org/en/download . Prefer a current supported LTS runtime.

## Evidence labels

**Ran locally:** clean-folder dependency installation; Chromium installation and launch; CLI manifest validation; offline test suite; first-run and changed-input HTML report rendering.

**Mock:** TikTok page-response fixtures used in tests. These prove parsing, ID isolation, block handling, missing-data behavior and visible changed-input output. They are not real account analytics.

**Checked against source and docs:** signed-in Studio response flow, current official analytics paths and the optional Accounts API schema.

**Not exercised:** authenticated live collection with a fresh reader's TikTok account. The package contains no login. A real first-post verification is explicitly part of setup before the reader's agent calls it ready.
