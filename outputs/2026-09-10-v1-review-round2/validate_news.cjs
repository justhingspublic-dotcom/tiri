const fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'../..');
const events=JSON.parse(fs.readFileSync(path.join(__dirname,'活動紀錄.json'),'utf8'));
const code=fs.readFileSync(path.join(root,'v1/js/news-round2.js'),'utf8');
function render(date){
 const nodes={'news-events':{textContent:JSON.stringify(events)},'news-recent-content':{},'news-archive-content':{}};
 const RealDate=Date;
 class FixedDate extends RealDate{constructor(...args){super(...(args.length?args:[date]));}}
 vm.runInNewContext(code,{document:{getElementById:id=>nodes[id]},Intl,Date:FixedDate});
 return {recent:nodes['news-recent-content'].innerHTML,archive:nodes['news-archive-content'].innerHTML};
}
const now=render('2026-09-10T03:00:00Z');
const future=render('2027-01-01T03:00:00Z');
function assert(ok,msg){if(!ok)throw Error(msg);}
assert((now.recent.match(/class="news-recent-card"/g)||[]).length===2,'Two current/future cards on review date');
assert((now.archive.match(/class="event-banner-row/g)||[]).length===151,'151 past events on review date');
assert(now.recent.includes('2026-09-10')&&!now.archive.includes('datetime="2026-09-10"'),'Today belongs only to upcoming');
assert(future.recent.includes('近期活動規劃中'),'Empty upcoming state');
assert((future.archive.match(/class="event-banner-row/g)||[]).length===153,'Every event moves to archive as time passes');
assert((now.archive.match(/archive-text-row/g)||[]).length===17,'No image invented for 17 historical records');
fs.writeFileSync(path.join(__dirname,'source/news-rendered.json'),JSON.stringify(now));
console.log('News date-boundary and event preservation checks: 6 passed.');
