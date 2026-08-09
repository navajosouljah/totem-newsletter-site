#!/usr/bin/env node
// build_emails.mjs - deterministic Market Pulse email builder (Totem LC Group)
//
// Usage:
//   node scripts/build_emails.mjs scripts/email_data.json          # writes into email_copy.html
//   node scripts/build_emails.mjs scripts/email_data.json --dry    # writes /tmp/email_copy_preview.html
//
// Regenerates the member + non-member Market Pulse teaser emails and the
// suggested-subject-lines block inside email_copy.html from a single JSON
// data file. This enforces two locked laws mechanically:
//   1. Emails are built FROM the article's numbers (the data file), never from memory.
//   2. Every subscriber link points to the LIVE domain (totem-challenge-preview) only.
//
// Covers the daily/weekly Market Pulse teaser formats (public + member edition).
// The Friday member email (Challenge-lead format) is a different locked layout
// and is NOT built by this script.

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const LIVE = 'https://totem-challenge-preview.vercel.app';

// ---------- load + validate data ----------
const dataPath = process.argv[2];
const dry = process.argv.includes('--dry');
if (!dataPath) die('Usage: node scripts/build_emails.mjs <data.json> [--dry]');
const d = JSON.parse(readFileSync(resolve(dataPath), 'utf8'));

const REQUIRED = ['edition_file', 'day_date', 'date_label', 'headline_short', 'preheader',
  'lead', 'bullets', 'subjects'];
for (const k of REQUIRED) if (!(k in d)) die(`Missing required field: ${k}`);
if (!/^market_pulse_[a-z0-9_]+\.html$/.test(d.edition_file)) die(`edition_file looks wrong: ${d.edition_file}`);
if (!d.lead.headline || !d.lead.context || !d.lead.link_text || !d.lead.link_anchor) die('lead needs headline, context, link_text, link_anchor');
if (!Array.isArray(d.bullets) || d.bullets.length < 4 || d.bullets.length > 6) die('bullets must be 4-6 items');
for (const b of d.bullets) if (!b.bold || !b.rest) die('each bullet needs bold + rest');
if (!Array.isArray(d.subjects) || d.subjects.length !== 3) die('subjects must be exactly 3 [{subject, note}]');

const ART = `${LIVE}/${d.edition_file}`;

// compliance scan on all copy fields
const allCopy = JSON.stringify(d);
if (allCopy.includes('\u2014')) die('Em dash found in data. Use " - " instead. (LOCKED rule)');
if (allCopy.includes('totem-newsletter-site')) die('Banned domain totem-newsletter-site in data. (LOCKED rule)');
for (const w of ['skyrocket', 'plunge', 'crash', 'brace for impact', 'maxed out']) {
  if (allCopy.toLowerCase().includes(w)) die(`Banned word "${w}" found in data.`);
}

// ---------- shared fragments ----------
const F_SANS = "'Inter', Helvetica, Arial, sans-serif";
const F_SERIF = "'Spectral', Georgia, 'Times New Roman', serif";

const head = (title) => `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>${title}</title>
<style type="text/css">
  body, table, td, p, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
  table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
  img { -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; }
  body { margin: 0 !important; padding: 0 !important; width: 100% !important; }
  .ExternalClass { width: 100%; }
  .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div { line-height: 100%; }
  @media only screen and (max-width: 600px) {
    .container { width: 100% !important; max-width: 100% !important; }
    .px-mobile { padding-left: 22px !important; padding-right: 22px !important; }
    .contact-cell { display: block !important; width: 100% !important; padding-bottom: 12px !important; }
  }
</style>
</head>
<body style="margin: 0 !important; padding: 0 !important; background-color: #f7f8fa; font-family: ${F_SANS};">

<div style="display: none; max-height: 0; overflow: hidden; mso-hide: all; font-size: 1px; line-height: 1px; color: #f7f8fa;">
  ${d.preheader}
</div>

<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f7f8fa;">
  <tr>
    <td align="center" style="padding: 32px 16px;">
      <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="600" class="container" style="max-width: 600px; background-color: #FFFFFF;">
`;

const masthead = (size, tagSize) => `
        <tr>
          <td class="px-mobile" style="padding: 28px 36px 20px 36px; text-align: center;">
            <p style="margin: 0 0 6px 0; font-family: ${F_SERIF}; font-size: ${size}px; font-weight: 800; letter-spacing: -0.02em; color: #16181d; line-height: 1;">TOTEM <span style="color: #032165;">LC GROUP</span></p>
            <p style="margin: 0; font-family: ${F_SANS}; font-size: ${tagSize}px; font-weight: 700; letter-spacing: 0.28em; text-transform: uppercase; color: #b8860b;">Funding Execution, Not Expectation</p>
          </td>
        </tr>
`;

// LOCKED (JJ, Aug 1 2026): hero card carries the SHORT title only, never the data-dump headline.
const hero = `
        <tr>
          <td class="px-mobile" style="padding: 0 36px;">
            <a href="${ART}" target="_blank" rel="noopener" style="text-decoration: none; color: inherit; display: block;">
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td style="background: linear-gradient(160deg, #04204f 0%, #032165 46%, #01102f 100%); padding: 32px 32px 28px 32px; border-radius: 4px 4px 0 0; text-align: center;">
                    <p style="margin: 0 0 6px 0; font-family: ${F_SANS}; font-size: 8px; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; color: rgba(255,255,255,0.50);">${d.day_date} &middot; Weekly Briefing</p>
                    <p style="margin: 0 0 4px 0; font-family: ${F_SANS}; font-size: 8px; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; color: rgba(255,255,255,0.35);">Totem LC Group &middot; Your Friend in the News</p>
                    <p style="margin: 0; font-family: ${F_SERIF}; font-weight: 800; font-size: 36px; line-height: 1; color: #ffffff; letter-spacing: -0.02em;">Market <span style="color: #fcb900;">Pulse</span></p>
                  </td>
                </tr>
              </table>
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="border: 1px solid #e4e6ea; border-top: none; background-color: #ffffff; border-radius: 0 0 4px 4px;">
                <tr>
                  <td style="padding: 20px 24px 8px 24px; text-align: center;">
                    <p style="margin: 0 0 6px 0; font-family: 'Spectral', Georgia, serif; font-size: 20px; font-weight: 700; line-height: 1.3; color: #16181d;">${d.headline_short}</p>
                    <p style="margin: 0; font-family: ${F_SANS}; font-size: 11px; color: #6b7280;">${d.day_date}</p>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 14px 24px 22px 24px; text-align: center;">
                    <span style="display: inline-block; background-color: #032165; border-radius: 3px; padding: 14px 32px; font-family: ${F_SANS}; font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #ffffff;">Read Today's Market Pulse</span>
                  </td>
                </tr>
              </table>
            </a>
          </td>
        </tr>
`;

// LOCKED: the lead owns ONE story and its numbers.
const lead = `
        <tr><td style="height: 24px;"></td></tr>
        <tr>
          <td class="px-mobile" style="padding: 0 36px 16px 36px;">
            <p style="margin: 0 0 14px 0; font-family: 'Spectral', Georgia, serif; font-size: 21px; font-weight: 700; line-height: 1.35; color: #16181d;">${d.lead.headline}</p>
            <p style="margin: 0; font-family: ${F_SANS}; font-size: 14px; line-height: 1.65; color: #26292f;">${d.lead.context}</p>
          </td>
        </tr>
        <tr>
          <td style="padding: 0 36px 28px 36px; text-align: center;">
            <a href="${ART}#${d.lead.link_anchor}" target="_blank" rel="noopener" style="font-family: ${F_SANS}; font-size: 12px; font-weight: 700; color: #032165; text-decoration: none; letter-spacing: 0.04em;">${d.lead.link_text} &rarr;</a>
          </td>
        </tr>
`;

const bulletRow = (b, last) => `<tr>
                <td valign="top" width="20" style="padding-top: 2px;"><p style="margin: 0; font-family: 'Spectral', Georgia, serif; font-size: 16px; font-weight: 800; color: #b8860b; line-height: 1.65;">&bull;</p></td>
                <td style="padding-bottom: ${last ? '4px' : '12px'};"><p style="margin: 0; font-family: ${F_SANS}; font-size: 14px; line-height: 1.65; color: #26292f;"><strong>${b.bold}</strong> ${b.rest}</p></td>
              </tr>`;

const bullets = `
        <tr><td style="padding: 0 36px;"><hr style="border: none; height: 1px; background-color: #e4e6ea; margin: 0;"></td></tr>
        <tr><td style="height: 20px;"></td></tr>
        <tr>
          <td class="px-mobile" style="padding: 0 36px 12px 36px;">
            <p style="margin: 0; font-family: ${F_SANS}; font-size: 9px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #b8860b;">Also in This Week's Briefing</p>
          </td>
        </tr>
        <tr>
          <td class="px-mobile" style="padding: 0 36px 6px 36px;">
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
              ${d.bullets.map((b, i) => bulletRow(b, i === d.bullets.length - 1)).join('\n              ')}
            </table>
          </td>
        </tr>
        <tr><td style="height: 8px;"></td></tr>
        <tr>
          <td style="padding: 8px 36px 36px 36px; text-align: center;">
            <a href="${ART}" target="_blank" rel="noopener" style="display: inline-block; background-color: #032165; border-radius: 3px; padding: 16px 44px; font-family: ${F_SANS}; font-size: 13px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #ffffff; text-decoration: none;">Read the Full Briefing</a>
          </td>
        </tr>
`;

const publicFooter = `
        <tr><td style="padding: 0 36px;"><hr style="border: none; height: 1px; background-color: #e4e6ea; margin: 0;"></td></tr>
        <tr>
          <td class="px-mobile" style="padding: 16px 36px 4px 36px; text-align: center;">
            <p style="margin: 0; font-family: ${F_SANS}; font-size: 10px; color: #9aa0a8; line-height: 1.5;">A free weekly snapshot for the Totem community. General information only - not investment advice or a recommendation to buy or sell anything.</p>
          </td>
        </tr>
        <tr>
          <td style="padding: 8px 36px 24px 36px; text-align: center;">
            <p style="margin: 0 0 4px 0; font-family: ${F_SERIF}; font-size: 16px; font-weight: 800; color: #16181d;">Totem <span style="color: #032165;">LC Group</span></p>
            <p style="margin: 0; font-family: ${F_SANS}; font-size: 10px; color: #9aa0a8;"><a href="https://totemlcg.com" style="color: #b8860b; text-decoration: none;">totemlcg.com</a></p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>`;

const memberDateBar = `
        <tr>
          <td style="background-color: #032165; padding: 10px 36px; text-align: center;">
            <p style="margin: 0; font-family: ${F_SANS}; font-size: 10px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: #ffffff;">${d.day_date} &nbsp;&middot;&nbsp; Member Edition</p>
          </td>
        </tr>
        <tr><td style="height: 20px;"></td></tr>
`;

const contact = `
        <tr><td style="padding: 0 36px;"><hr style="border: none; height: 1px; background-color: #e4e6ea; margin: 0;"></td></tr>
        <tr>
          <td class="px-mobile" style="padding: 24px 36px 6px 36px; text-align: center;">
            <p style="margin: 0 0 6px 0; font-family: 'Spectral', Georgia, serif; font-size: 20px; font-weight: 800; color: #16181d; line-height: 1.25;">Questions about a transaction or your membership?</p>
            <p style="margin: 0 0 20px 0; font-family: ${F_SANS}; font-size: 13px; line-height: 1.5; color: #6b7280;">You are a member, not a ticket number. Call or email the desk and a person answers.</p>
          </td>
        </tr>
        <tr>
          <td class="px-mobile" style="padding: 0 36px 16px 36px;">
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
              <tr>
                <td class="contact-cell" width="50%" valign="top" style="padding-right: 6px; text-align: center;">
                  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr><td style="background-color: #032165; border-radius: 4px; padding: 16px 12px; text-align: center;"><a href="tel:+12089960435" style="font-family: ${F_SANS}; font-size: 15px; font-weight: 700; color: #ffffff; text-decoration: none; letter-spacing: 0.02em;">(208) 996-0435</a></td></tr>
                    <tr><td style="padding-top: 8px; text-align: center;"><p style="margin: 0; font-family: ${F_SANS}; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #6b7280;">Call the Team</p></td></tr>
                  </table>
                </td>
                <td class="contact-cell" width="50%" valign="top" style="padding-left: 6px; text-align: center;">
                  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr><td style="background-color: #032165; border-radius: 4px; padding: 16px 12px; text-align: center;"><a href="mailto:partnership@totemlcg.com" style="font-family: ${F_SANS}; font-size: 13px; font-weight: 700; color: #ffffff; text-decoration: none; letter-spacing: 0.01em;">partnership@totemlcg.com</a></td></tr>
                    <tr><td style="padding-top: 8px; text-align: center;"><p style="margin: 0; font-family: ${F_SANS}; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #6b7280;">Email the Desk</p></td></tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td class="px-mobile" style="padding: 0 36px 28px 36px; text-align: center;">
            <p style="margin: 0; font-family: ${F_SANS}; font-size: 9px; font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; color: #b8860b;">Funding Execution, Not Expectation</p>
          </td>
        </tr>
        <tr><td style="padding: 0 36px;"><hr style="border: none; height: 1px; background-color: #e4e6ea; margin: 0;"></td></tr>
        <tr>
          <td class="px-mobile" style="padding: 16px 36px 4px 36px; text-align: center;">
            <p style="margin: 0; font-family: ${F_SANS}; font-size: 10px; color: #9aa0a8; line-height: 1.5;">You are receiving this email as a member of Totem LC Group.</p>
          </td>
        </tr>
        <tr>
          <td style="padding: 8px 36px 24px 36px; text-align: center;">
            <p style="margin: 0 0 4px 0; font-family: ${F_SERIF}; font-size: 16px; font-weight: 800; color: #16181d;">Totem <span style="color: #032165;">LC Group</span></p>
            <p style="margin: 0; font-family: 'Courier New', Courier, monospace; font-size: 9px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #b8860b;">Home of 20% Returns</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>`;

// ---------- assemble ----------
const nonmember = head(`Market Pulse - ${d.date_label}`) + masthead(28, 8) + hero + lead + bullets + publicFooter;
const member = head(`Market Pulse - ${d.date_label} - Member Edition`) + masthead(36, 10) + memberDateBar + hero + lead + bullets + contact;

// ---------- output validation ----------
for (const [name, html] of [['member', member], ['nonmember', nonmember]]) {
  if (html.includes('\u2014')) die(`em dash leaked into ${name}`);
  if (html.includes('`')) die(`backtick in ${name} (breaks the JS template literal)`);
  const hrefs = [...html.matchAll(/href="([^"]+)"/g)].map(m => m[1]);
  for (const h of hrefs) {
    if (!(h.startsWith(LIVE) || h.startsWith('tel:') || h.startsWith('mailto:') || h === 'https://totemlcg.com'))
      die(`illegal link in ${name}: ${h}`);
  }
}

// ---------- subject lines block ----------
const subjectRow = (s, i) => `      <div style="${i ? "border-top:1px solid #e4e6ea;padding-top:10px;" : ""}display:flex;align-items:flex-start;gap:12px;">
        <span style="font-family:'Work Sans',sans-serif;font-size:10px;font-weight:700;color:#9aa0a8;min-width:20px;padding-top:3px;">${'ABC'[i]}</span>
        <div>
          <p style="margin:0;font-family:'Spectral',Georgia,serif;font-size:17px;font-weight:700;color:#16181d;line-height:1.3;">${s.subject}</p>
          <p style="margin:4px 0 0;font-family:'Work Sans',sans-serif;font-size:11px;color:#9aa0a8;">${s.note}</p>
        </div>
      </div>`;

const subjectBlock = `<!-- SUBJECT LINE SUGGESTIONS -->
  <div style="background:#f7f8fa;border:1px solid #e4e6ea;border-radius:4px;padding:24px 28px;margin-bottom:28px;">
    <div style="font-family:'Work Sans',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#b8860b;margin-bottom:14px;">Suggested Subject Lines - ${d.date_label}</div>
    <div style="display:flex;flex-direction:column;gap:10px;">
${d.subjects.map(subjectRow).join('\n')}
    </div>
  </div>

  `;

// ---------- inject into email_copy.html ----------
const target = resolve(ROOT, 'email_copy.html');
let page = readFileSync(target, 'utf8');

const rx = {
  member: /var memberEmailHTML=`[\s\S]*?`;/,
  nonmember: /var nonMemberEmailHTML=`[\s\S]*?`;/,
  subjects: /<!-- SUBJECT LINE SUGGESTIONS -->[\s\S]*?(?=<!-- AUDIENCE TABS -->)/,
  nav: /<li><a href="market_pulse_[a-z0-9_]+\.html">Market Pulse<\/a><\/li>/,
};
for (const [k, r] of Object.entries(rx)) if (!r.test(page)) die(`Anchor not found in email_copy.html: ${k}`);

page = page
  .replace(rx.subjects, subjectBlock)
  .replace(rx.nav, `<li><a href="${d.edition_file}">Market Pulse</a></li>`)
  .replace(rx.member, 'var memberEmailHTML=`' + member + '`;')
  .replace(rx.nonmember, 'var nonMemberEmailHTML=`' + nonmember + '`;');

const out = dry ? '/tmp/email_copy_preview.html' : target;
writeFileSync(out, page);
console.log(`OK  wrote ${out}`);
console.log(`    member ${(member.length / 1024).toFixed(1)}K | nonmember ${(nonmember.length / 1024).toFixed(1)}K | bullets ${d.bullets.length} | links -> ${LIVE}`);

function die(msg) { console.error('FAIL  ' + msg); process.exit(1); }
