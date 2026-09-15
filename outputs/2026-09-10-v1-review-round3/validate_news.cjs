const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..');
const events=JSON.parse(fs.readFileSync(path.join(__dirname,'活動紀錄.json'),'utf8'));
const old=JSON.parse(fs.readFileSync(path.join(__dirname,'../2026-09-10-v1-review-round2/活動紀錄.json'),'utf8'));
const code=fs.readFileSync(path.join(root,'v1/js/news-round2.js'),'utf8');
function render(date){
 const nodes={'news-events':{textContent:JSON.stringify(events)},'news-recent-content':{},'news-archive-content':{}};
 const RealDate=Date;
 class FixedDate extends RealDate{constructor(...args){super(...(args.length?args:[date]));}}
 vm.runInNewContext(code,{document:{getElementById:id=>nodes[id]},Intl,Date:FixedDate});
 return {recent:nodes['news-recent-content'].innerHTML,archive:nodes['news-archive-content'].innerHTML};
}
const now=render('2026-09-10T03:00:00Z'),future=render('2027-01-01T03:00:00Z');
assert.deepEqual(events.slice(0,old.length),old,'Preserve all 153 original records verbatim');
assert.equal(events.length,157);
assert.equal((now.recent.match(/class="news-recent-card"/g)||[]).length,5);
assert.equal((now.archive.match(/class="event-banner-row/g)||[]).length,152);
assert(!now.recent.includes('datetime="2026-09-10"')&&now.archive.includes('datetime="2026-09-10"'));
assert.deepEqual([...now.recent.matchAll(/datetime="(.*?)"/g)].map(x=>x[1]),['2026-09-18','2026-10-02','2026-10-16','2026-10-23','2026-11-13']);
assert(future.recent.includes('近期活動規劃中'));
assert.equal((future.archive.match(/class="event-banner-row/g)||[]).length,157);
assert.equal((now.archive.match(/archive-text-row/g)||[]).length,17);
assert(render('2026-09-17T15:59:59Z').recent.includes('datetime="2026-09-18"'));
assert(!render('2026-09-17T16:00:00Z').recent.includes('datetime="2026-09-18"'),'Taipei midnight moves today into archive');
const recentIds=[...now.recent.matchAll(/href="https:\/\/www.accupass.com\/event\/(\d+)"/g)].map(x=>x[1]);
assert.equal(new Set(recentIds).size,5);
fs.writeFileSync(path.join(__dirname,'source/news-rendered.json'),JSON.stringify(now));
console.log('News: 12 preservation, completeness and Taipei date-boundary assertions passed.');
