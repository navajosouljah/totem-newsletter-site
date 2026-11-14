import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {parseRetention,summarize,requestMatchesItem,pullRetention} from '../pull.js';
import {validateManifest,alignCurve} from '../manifest.js';
import {renderReport} from '../collector.js';
const example=JSON.parse(fs.readFileSync(new URL('../clips.example.json',import.meta.url)));
const id=example[0].post_id;
const payload={video_info:{item_id:id},video_retention_rate_realtime:{value:{list:[{timestamp:0,value:1},{timestamp:1500,value:.8},{timestamp:3000,value:.5}]}},realtime_total_video_views:{value:{value:100}}};
function fake(response,{status=200,responseId=id}={}){
  let handler;
  const page={on(e,h){handler=h;},off(){},async goto(){await handler({request:()=>({url:()=>`https://www.tiktok.com/aweme/v2/data/insight/?aweme_id=${responseId}`}),status:()=>status,text:async()=>JSON.stringify(response)});return {status:()=>200};},url:()=>`https://www.tiktok.com/tiktokstudio/analytics/${id}`,locator:()=>({innerText:async()=>''}),close:async()=>{}};
  return {newPage:async()=>page,cookies:async()=>[{name:'sessionid'}]};
}
test('retention keeps exact fractional seconds and null metrics',()=>{
  const curve=parseRetention(payload);
  assert.equal(curve[1].second,1.5);
  assert.equal(curve[2].retained_fraction,.5);
  assert.equal(summarize(payload).average_watch_seconds,null);
});
test('empty, malformed and duplicate-time curves never become zeros',()=>{
  assert.deepEqual(parseRetention({}),[]);
  assert.deepEqual(parseRetention({video_retention_rate_realtime:{value:{list:[{timestamp:0,value:null}]}}}),[]);
  assert.deepEqual(parseRetention({video_retention_rate_realtime:{value:{list:[{timestamp:0,value:1},{timestamp:0,value:.8}]}}}),[]);
});
test('strict request join rejects mixed and wrong IDs',()=>{
  const url='https://www.tiktok.com/aweme/v2/data/insight/?type_requests='+encodeURIComponent(JSON.stringify([{aweme_id:id,insigh_type:'video_retention_rate_realtime'}]));
  assert.equal(requestMatchesItem(url,id),true);
  assert.equal(requestMatchesItem(url,'9999999999999999999'),false);
  assert.equal(requestMatchesItem(url+'&item_id=999', '999'),false);
  const mixed='https://www.tiktok.com/aweme/v2/data/insight/?type_requests='+encodeURIComponent(JSON.stringify([{aweme_id:id},{aweme_id:'9999999999999999999'}]));
  assert.equal(requestMatchesItem(mixed,id),false);
});
test('one observation uses the page response and joins the actual clip',async()=>{
  const r=await pullRetention(fake(payload),id,{waitMs:0});
  assert.equal(r.ok,true);
  const aligned=alignCurve(r.curve,example[0]);
  assert.equal(aligned[1].source_second,91.5);
  assert.ok(Math.abs(aligned[1].percentage_point_drop-20)<1e-10);
  assert.equal(aligned[2].source_second,80);
  assert.equal(aligned[2].words_playing,example[0].transcript[1].text);
});
test('wrong response ID and wrong payload ID cannot contaminate a clip',async()=>{
  assert.equal((await pullRetention(fake(payload,{responseId:'9999999999999999999'}),id,{waitMs:0})).ok,false);
  const wrong=structuredClone(payload);wrong.video_info.item_id='9999999999999999999';
  assert.equal((await pullRetention(fake(wrong),id,{waitMs:0})).ok,false);
});
test('block stops the read, with no retry or fictional curve',async()=>{
  const r=await pullRetention(fake({message:'Too many requests'},{status:429}),id,{waitMs:0});
  assert.equal(r.ok,false);assert.equal(r.blocked,true);assert.equal(r.reason,'http-429');
});
test('empty retention is unavailable, not success',async()=>{
  assert.equal((await pullRetention(fake({}),id,{waitMs:0})).reason,'retention-unavailable-or-schema-changed');
});
test('manifest rejects duplicate IDs, numeric IDs, gaps and missing timezone',()=>{
  assert.throws(()=>validateManifest([example[0],example[0]]),/Duplicate/);
  const numeric=structuredClone(example);numeric[0].post_id=1234567890123456789;
  assert.throws(()=>validateManifest(numeric),/quoted string/);
  const gap=structuredClone(example);gap[0].time_map[1].clip_start=4;
  assert.throws(()=>validateManifest(gap),/gaps/);
  const timezone=structuredClone(example);timezone[0].published_at='2026-10-30T12:00:00';
  assert.throws(()=>validateManifest(timezone),/timezone/);
});
test('returning reader changed words and source map reach visible HTML',()=>{
  const old=structuredClone(example[0]);
  const changed=structuredClone(old);changed.transcript[1].text='A changed answer from the returning reader';changed.time_map[1].source_start=180;changed.time_map[1].source_end=187;
  const make=c=>({clip_id:c.clip_id,post_id:c.post_id,post_url:c.post_url,status:'collected',collected_at:'fixture',summary:{views:100},aligned_curve:alignCurve(parseRetention(payload),c)});
  const first=renderReport([make(old)]),second=renderReport([make(changed)]);
  assert.ok(!first.includes('A changed answer from the returning reader'));
  assert.ok(second.includes('A changed answer from the returning reader'));
  assert.ok(second.includes('180s'));
  fs.mkdirSync(new URL('../test-results/',import.meta.url),{recursive:true});
  fs.writeFileSync(new URL('../test-results/first-run.html',import.meta.url),first);
  fs.writeFileSync(new URL('../test-results/returning-reader.html',import.meta.url),second);
});
