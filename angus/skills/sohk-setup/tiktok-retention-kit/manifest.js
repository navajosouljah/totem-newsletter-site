import fs from 'node:fs';

export function validateManifest(value) {
  if (!Array.isArray(value) || value.length < 1 || value.length > 10) {
    throw new Error('The manifest must contain 1–10 posted clips. Start with one.');
  }
  const seen = new Set();
  return value.map((c) => {
    if (typeof c.post_id !== 'string' || !/^\d{10,30}$/.test(c.post_id)) throw new Error('Each post_id must be the exact TikTok ID as a quoted string.');
    if (seen.has(c.post_id)) throw new Error('Duplicate post_id: ' + c.post_id);
    seen.add(c.post_id);
    if (!c.clip_id || !c.interview_id || !c.export_file) throw new Error('Each clip needs clip_id, interview_id and export_file.');
    const u = new URL(c.post_url);
    if (!['www.tiktok.com', 'tiktok.com'].includes(u.hostname) || u.pathname.split('/').pop() !== c.post_id) throw new Error('post_url must be the full TikTok video URL for post_id.');
    if (!Number.isFinite(Date.parse(c.published_at))) throw new Error('published_at must be an ISO date with timezone.');
    if (!/([zZ]|[+-]\d{2}:\d{2})$/.test(c.published_at)) throw new Error('published_at must include a timezone.');
    if (!Array.isArray(c.time_map) || !c.time_map.length) throw new Error('time_map must describe the actual exported edit.');
    let lastEnd = 0;
    for (const t of c.time_map) {
      if (![t.clip_start,t.clip_end,t.source_start,t.source_end].every(Number.isFinite)) throw new Error('Time-map seconds must be numbers.');
      if (t.clip_start < 0 || t.source_start < 0 || t.clip_end <= t.clip_start || t.source_end <= t.source_start) throw new Error('Invalid time-map interval.');
      if (Math.abs(t.clip_start - lastEnd) > 0.001) throw new Error('Time map must cover the export from second 0 with no gaps or overlaps.');
      if (Math.abs((t.clip_end-t.clip_start)-(t.source_end-t.source_start)) > 0.001) throw new Error('This time map supports normal-speed footage. Export an exact mapping for speed changes.');
      lastEnd = t.clip_end;
    }
    if (!Array.isArray(c.transcript)) throw new Error('transcript must be an array of the actual exported clip’s timestamped lines.');
    for (const t of c.transcript) {
      if (!Number.isFinite(t.start) || !Number.isFinite(t.end) || t.start < 0 || t.end <= t.start || t.end > lastEnd + 0.01 || typeof t.text !== 'string') throw new Error('Invalid exported-clip transcript line.');
    }
    return c;
  });
}

export function readManifest(file) {
  return validateManifest(JSON.parse(fs.readFileSync(file, 'utf8')));
}

export function alignCurve(curve, clip) {
  return curve.map((p, i) => {
    const end = clip.time_map.at(-1).clip_end;
    const mapping = clip.time_map.find(t => p.second >= t.clip_start && (p.second < t.clip_end || p.second === end && p.second === t.clip_end));
    const speech = clip.transcript.filter(t => p.second >= t.start && p.second < t.end).map(t => t.text).join(' ') || null;
    const before = i ? curve[i-1] : null;
    return {
      ...p,
      source_second: mapping ? mapping.source_start + p.second - mapping.clip_start : null,
      words_playing: speech,
      interval_start_second: before?.second ?? null,
      percentage_point_drop: before ? (before.retained_fraction-p.retained_fraction)*100 : null,
    };
  });
}
