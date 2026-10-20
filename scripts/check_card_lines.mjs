// For each card group, report how many lines each title/text takes, and flag short last lines (orphans).
import { chromium } from 'playwright';
const pages = { '/': ['.finder .finder-btn', '.jump-rail .xc-title', '.home-sec .path-grid .xc-title', '.home-sec .path-grid .xc-text', '.home-sec .amend-grid .xc-title', '.home-sec .article-list .xc-title', '.more-row .mini-card'],
  '/situations/': ['.sit-grid .xc-title', '.sit-grid .xc-text'],
  '/paths/': ['.path-grid .xc-title', '.path-grid .xc-text'],
  '/articles/': ['.article-list .xc-title', '.article-list .xc-text'],
  '/amendments/': ['.amend-grid .xc-title'] };
const b = await chromium.launch({executablePath: process.env.CHROME});
for (const [w, tag] of [[1440,'desktop'],[1280,'laptop'],[1100,'1100'],[1024,'small laptop'],[960,'960'],[820,'tablet'],[768,'768'],[640,'large phone'],[390,'phone'],[360,'small phone']]) {
  const p = await b.newPage({viewport:{width:w,height:900}});
  console.log(`\n=== ${tag} ${w}px ===`);
  for (const [u, sels] of Object.entries(pages)) {
    await p.goto('http://localhost:8790'+u);
    for (const sel of sels) {
      const r = await p.evaluate((sel)=>[...document.querySelectorAll(sel)].map(el=>{
        const rg=document.createRange(); rg.selectNodeContents(el);
        const rects=[...rg.getClientRects()].filter(r=>r.width>1);
        const tops=[...new Set(rects.map(r=>Math.round(r.top)))].sort((a,b)=>a-b);
        const lines=tops.length; const last=rects.filter(r=>Math.round(r.top)===tops[tops.length-1]);
        const lastW=last.reduce((s,r)=>s+r.width,0); const boxW=el.getBoundingClientRect().width;
        const orphan = lines>1 && lastW < boxW*0.3;
        return {t:el.textContent.trim().slice(0,38), lines, orphan};
      }), sel);
      const counts=[...new Set(r.map(x=>x.lines))].sort();
      const orph=r.filter(x=>x.orphan).map(x=>x.t);
      const flag = (counts.length>1 || orph.length) ? '  <-- ' : '';
      console.log(`${u} ${sel}: lines ${JSON.stringify(r.map(x=>x.lines))}${orph.length?' orphans: '+orph.join(' | '):''}${flag}`);
    }
  }
}
await b.close();
