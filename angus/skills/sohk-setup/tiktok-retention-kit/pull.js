// Derived from the TikTok Sync Studio response capture supplied with the guide.
// Reads the page's own response; no private-endpoint replay or cookie manipulation.
const BLOCK_HTTP_STATUSES = new Set([401, 403, 429]);
const BLOCK_URL_PATTERN = /\/(?:captcha|verify|challenge|login)(?:[/?#]|$)|security[-_]?check/i;
const BLOCK_TEXT_PATTERN = /captcha|security check|verify (?:to continue|it(?:'|’)s you|your identity)|too many requests|unusual activity|access denied|temporarily blocked/i;

export function detectBlockSignal({status=200,url='',bodyText='',payload=null}={}) {
  if (BLOCK_HTTP_STATUSES.has(Number(status))) return 'http-'+status;
  if (BLOCK_URL_PATTERN.test(url)) return 'redirect:'+new URL(url,'https://www.tiktok.com').pathname;
  const message=[payload?.status_msg,payload?.status_message,payload?.message,payload?.error?.message,bodyText].filter(Boolean).join(' ');
  return BLOCK_TEXT_PATTERN.test(message) ? 'challenge-response' : null;
}

export function parseRetention(insight) {
  const rows=insight?.video_retention_rate_realtime?.value?.list;
  if (!Array.isArray(rows) || !rows.length) return [];
  const curve=rows.map(p=>({second:Number(p.timestamp)/1000,retained_fraction:Number(p.value)}));
  // Reject a changed or partial schema; never round, interpolate or zero-fill it.
  if (rows.some(p=>p.timestamp == null || p.value == null) || curve.some(p=>!Number.isFinite(p.second) || p.second<0 || !Number.isFinite(p.retained_fraction) || p.retained_fraction<0 || p.retained_fraction>1)) return [];
  curve.sort((a,b)=>a.second-b.second);
  if (curve.some((p,i)=>i && p.second===curve[i-1].second)) return [];
  return curve;
}

export function summarize(insight) {
  const num=k=>{const v=insight?.[k]?.value?.value; return v!=null && Number.isFinite(Number(v)) ? Number(v) : null;};
  return {
    views:num('realtime_total_video_views'),
    full_watch_fraction:num('video_finish_rate_realtime'),
    average_watch_seconds:num('video_per_duration_realtime'),
    total_watch_seconds:num('video_total_duration_realtime'),
    new_followers:num('realtime_new_followers'),
    after_seven_days:insight?.video_retention_rate_realtime?.is_after_7d ?? null,
  };
}

export function requestMatchesItem(url,itemId) {
  try {
    const u=new URL(url);
    if (!/(^|\.)tiktok\.com$/.test(u.hostname) || !/\/aweme\/v2\/data\/insight\//.test(u.pathname)) return false;
    const requests=JSON.parse(u.searchParams.get('type_requests') || 'null');
    if (Array.isArray(requests)) {
      const ids=[...new Set(requests.map(x=>String(x.aweme_id || '')).filter(Boolean))];
      return ids.length===1 && ids[0]===itemId;
    }
    return u.searchParams.get('aweme_id')===itemId || u.searchParams.get('item_id')===itemId;
  } catch {return false;}
}

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
export async function pullRetention(context,itemId,{waitMs=15000}={}) {
  const page=await context.newPage();
  let insight=null,blocked=null;
  const pending=new Set();
  const onResponse=resp=>{
    if (!requestMatchesItem(resp.request().url(),itemId)) return;
    const task=(async()=>{
      const text=await resp.text().catch(()=> '');
      let data=null;
      try{data=JSON.parse(text);}catch{}
      blocked ||= detectBlockSignal({status:resp.status(),url:resp.request().url(),bodyText:data?'':text.slice(0,1000),payload:data});
      const payloadId=data?.video_info?.item_id ?? data?.video_info?.aweme_id ?? data?.video_info?.id;
      if (payloadId != null && String(payloadId)!==itemId) return;
      if (data?.video_retention_rate_realtime) insight=data;
    })().finally(()=>pending.delete(task));
    pending.add(task);
  };
  page.on('response',onResponse);
  try {
    const navigation=await page.goto('https://www.tiktok.com/tiktokstudio/analytics/'+itemId,{waitUntil:'domcontentloaded'});
    blocked ||= detectBlockSignal({status:navigation?.status() ?? 200,url:page.url()});
    for(let elapsed=0;elapsed<waitMs && !insight && !blocked;elapsed+=500) await sleep(500);
    await Promise.allSettled([...pending]);
    const text=await page.locator('body').innerText({timeout:1500}).catch(()=> '');
    blocked ||= detectBlockSignal({url:page.url(),bodyText:text.slice(0,6000)});
    if(blocked) return {ok:false,reason:blocked,blocked:true};
    if(!(await context.cookies('https://www.tiktok.com')).some(c=>c.name==='sessionid')) return {ok:false,reason:'logged-out',blocked:true};
    const curve=parseRetention(insight);
    if(!curve.length) return {ok:false,reason:'retention-unavailable-or-schema-changed'};
    return {ok:true,curve,summary:summarize(insight)};
  } finally {
    page.off('response',onResponse);
    await page.close().catch(()=>{});
  }
}
