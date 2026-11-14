import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomUUID} from 'node:crypto';
import {chromium} from 'playwright';
import {readManifest,alignCurve} from './manifest.js';
import {pullRetention} from './pull.js';
const ROOT=path.dirname(fileURLToPath(import.meta.url));
const PROFILE=path.join(ROOT,'.profile');
const OUT=path.join(ROOT,'results');
const LOCK=path.join(ROOT,'.run.lock');
const command=process.argv[2] || 'help';
const manifestPath=path.resolve(process.argv[3] || path.join(ROOT,'clips.json'));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function help(){console.log(`Interview clip retention
node collector.js login                 Open your own isolated Studio login
node collector.js check [clips.json]    Validate the exact posted-clip manifest
node collector.js collect [clips.json]  Read 1–10 posts, save JSON and an HTML report
node collector.js help                  Show this help
No posts are uploaded or changed. No database or API key is required.`);}
const escape=s=>String(s??'Unknown').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function renderReport(records){
  const parts=records.map(r=>{
    const drops=(r.aligned_curve || []).filter(p=>p.percentage_point_drop>0).sort((a,b)=>b.percentage_point_drop-a.percentage_point_drop).slice(0,3);
    const rows=drops.map(p=>`<tr><td>${escape(p.interval_start_second)}–${escape(p.second)}s</td><td>${p.percentage_point_drop.toFixed(1)} pp</td><td>${escape(p.source_second)}s</td><td>${escape(p.words_playing)}</td></tr>`).join('');
    return `<article><h2>${escape(r.clip_id)}</h2><p><a href="${escape(r.post_url)}">Post ${escape(r.post_id)}</a> · ${escape(r.status)} · ${escape(r.collected_at)}</p><p>${escape(r.reason || '')}</p><p>Views: ${escape(r.summary?.views)} · Observed points: ${r.aligned_curve?.length || 0}</p><table><thead><tr><th>Clip interval</th><th>Drop</th><th>Source second at end</th><th>Words at interval end</th></tr></thead><tbody>${rows || '<tr><td colspan="4">No measured drop available.</td></tr>'}</tbody></table></article>`;
  }).join('\n');
  return `<!doctype html><html lang="en"><meta charset="utf-8"><title>Interview clip retention</title><style>body{font:16px/1.5 system-ui;max-width:1000px;margin:32px auto;padding:0 20px;color:#16130f;background:white}article{border:1px solid #e2ddd6;border-radius:14px;padding:20px;margin:20px 0}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #eee;text-align:left;padding:8px}a{color:#a95135}h1{font-size:32px}</style><h1>Interview clip retention</h1><p>${records.filter(r=>r.status==='collected').length}/${records.length} posts have observed curves. Drops identify intervals to inspect, not proof of why someone left. Replay the actual exported clip before changing it.</p>${parts}</html>`;
}

async function main(){
  if(['help','--help','-h'].includes(command)){help();return;}
  if(!['login','check','collect'].includes(command)) throw new Error('Unknown command. Run node collector.js help.');
  const clips=command==='login'?null:readManifest(manifestPath);
  if(command==='check'){console.log(`Manifest valid: ${clips.length} unique posted clips; time maps cover each export.`);return;}
  let lock;
  try{lock=fs.openSync(LOCK,'wx');fs.writeFileSync(lock,String(process.pid));}
  catch{throw new Error('Another collector may be running. Close that process first. If it crashed, check no collector browser remains, then delete .run.lock.');}
  let context;
  const close=async()=>{await context?.close().catch(()=>{});try{fs.closeSync(lock);}catch{}try{fs.unlinkSync(LOCK);}catch{}};
  let closing=false;
  for(const signal of ['SIGINT','SIGTERM']) process.once(signal,async()=>{if(closing)return;closing=true;await close();process.exit(130);});
  try{
    context=await chromium.launchPersistentContext(PROFILE,{headless:false,viewport:{width:1400,height:950}});
    if(command==='login'){
      const page=context.pages()[0] || await context.newPage();
      await page.goto('https://www.tiktok.com/tiktokstudio',{waitUntil:'domcontentloaded'});
      console.log('Sign in normally in this browser. Your agent can navigate to one recent post’s analytics. When finished, close this browser window. Your session stays in .profile on your computer.');
      await new Promise(resolve=>context.on('close',resolve));
      return;
    }
    fs.mkdirSync(OUT,{recursive:true});
    const runId=new Date().toISOString().replace(/[:.]/g,'-')+'-'+randomUUID().slice(0,8);
    const records=[];
    let stopReason=null,emptyCount=0;
    for(let i=0;i<clips.length;i++){
      const clip=clips[i];
      let result;
      if(stopReason) result={ok:false,reason:'not-attempted: '+stopReason};
      else{
        try{result=await pullRetention(context,clip.post_id);}catch(error){result={ok:false,reason:'read-error: '+error.message,blocked:true};}
        if(result.blocked) stopReason=result.reason;
        else if(!result.ok && ++emptyCount>=2) stopReason='two consecutive unavailable curves';
        else if(result.ok) emptyCount=0;
      }
      const record={schema_version:1,run_id:runId,interview_id:clip.interview_id,clip_id:clip.clip_id,post_id:clip.post_id,post_url:clip.post_url,published_at:clip.published_at,export_file:clip.export_file,collected_at:new Date().toISOString(),source:'tiktok-studio-page-response',status:result.ok?'collected':stopReason && result.reason.startsWith('not-attempted:')?'not-attempted':'unavailable',reason:result.reason ?? null,summary:result.summary ?? null,retention_curve:result.curve ?? null,aligned_curve:result.ok?alignCurve(result.curve,clip):null,time_map:clip.time_map};
      records.push(record);
      fs.writeFileSync(path.join(OUT,runId+'.json'),JSON.stringify(records,null,2));
      fs.writeFileSync(path.join(OUT,runId+'.html'),renderReport(records));
      console.log(`${clip.clip_id}: ${record.status}${record.reason?' ('+record.reason+')':''}`);
      if(i<clips.length-1 && !stopReason) await sleep(10000+Math.floor(Math.random()*8001));
    }
    console.log('Results: '+path.join(OUT,runId+'.html'));
    if(stopReason) console.log('Stopped new reads: '+stopReason+'. No retries or cookie resets were made.');
  }finally{await close();}
}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url))main().catch(e=>{console.error(e.message);process.exitCode=1;});
