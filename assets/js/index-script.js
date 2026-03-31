(function generateData(){
  const countries = [
    'United States','China','India','Russia','Japan','Germany','South Korea','Iran','Canada','Saudi Arabia',
    'United Kingdom','Brazil','Mexico','Australia','Indonesia','France','Italy','Turkey','Poland','South Africa',
    'Argentina','Kazakhstan','Thailand','Ukraine','Malaysia','Netherlands','Philippines','Pakistan','Egypt','Vietnam',
    'Bangladesh','Algeria','Nigeria','Colombia','Spain','Iraq','Venezuela','Uzbekistan','United Arab Emirates','Kuwait',
    'Belgium','Czech Republic','Qatar','Chile','Romania','Portugal','Sweden','Greece','Austria','Norway',
    'Denmark','Finland','Switzerland','Hungary','Belarus','New Zealand','Singapore','Israel','Ireland','Slovakia',
    'Libya','Peru','Ecuador','Bolivia','Cuba','Sri Lanka','Croatia','Myanmar','Morocco','Ethiopia',
    'Ghana','Tanzania','Kenya','Angola','Tunisia','Sudan','Oman','Azerbaijan','Turkmenistan','Bahrain',
    'Trinidad and Tobago','Cameroon','Ivory Coast','Zimbabwe','Zambia','Uganda','Mozambique','Senegal','Yemen','Jordan',
    'Panama','Dominican Republic','Costa Rica','Guatemala','Honduras','El Salvador','Paraguay','Uruguay','Jamaica','Cyprus',
  ];
  const BASE_CO2 = {'China':9500,'United States':5000,'India':2600,'Russia':1700,'Japan':1100,'Germany':750,'South Korea':620,'Iran':620,'Canada':560,'Saudi Arabia':620,'United Kingdom':440,'Brazil':490,'Mexico':450,'Australia':420,'Indonesia':580,'France':360,'Italy':340,'Turkey':400,'Poland':320,'South Africa':460};
  const GROWTH = {'China':0.07,'India':0.06,'Indonesia':0.05,'Vietnam':0.06,'Malaysia':0.04,'Saudi Arabia':0.04,'Iran':0.04,'Turkey':0.04,'Bangladesh':0.05,'Pakistan':0.04,'United States':-0.005,'Germany':-0.015,'United Kingdom':-0.02,'France':-0.01,'Russia':0.01,'Japan':-0.005,'South Korea':0.02,'Australia':0.005};
  const years = [];
  for(let y=1990;y<=2023;y++) years.push(y);
  const rand=(a,b)=>a+Math.random()*(b-a);
  const seed=(n)=>{let s=n;return ()=>(s=s*16807%2147483647,s/2147483647);};
  window.ALL_YEARS=years;
  window.ALL_COUNTRIES=countries;
  const compData=[],mapData=[],raceData=years.map(y=>({Year:y,Data:[]})),growthRaceData=years.slice(1).map(y=>({Year:y,Data:[]})),sankeyData=years.map(y=>({Year:y,Regions:{},TopEmitters:[]}));
  const regionMap={'United States':'North America','Canada':'North America','Mexico':'North America','Brazil':'South America','Argentina':'South America','Colombia':'South America','Peru':'South America','Chile':'South America','Venezuela':'South America','Ecuador':'South America','Bolivia':'South America','Paraguay':'South America','Uruguay':'South America','Germany':'Europe','United Kingdom':'Europe','France':'Europe','Italy':'Europe','Spain':'Europe','Poland':'Europe','Netherlands':'Europe','Turkey':'Europe','Ukraine':'Europe','Russia':'Europe','Belgium':'Europe','Czech Republic':'Europe','Sweden':'Europe','Greece':'Europe','Austria':'Europe','Norway':'Europe','Denmark':'Europe','Finland':'Europe','Switzerland':'Europe','Hungary':'Europe','Portugal':'Europe','Romania':'Europe','Slovakia':'Europe','Ireland':'Europe','Croatia':'Europe','Belarus':'Europe','China':'Asia','India':'Asia','Japan':'Asia','South Korea':'Asia','Indonesia':'Asia','Iran':'Asia','Saudi Arabia':'Asia','Malaysia':'Asia','Pakistan':'Asia','Bangladesh':'Asia','Vietnam':'Asia','Kazakhstan':'Asia','Uzbekistan':'Asia','United Arab Emirates':'Asia','Kuwait':'Asia','Qatar':'Asia','Iraq':'Asia','Thailand':'Asia','Philippines':'Asia','Myanmar':'Asia','Sri Lanka':'Asia','Azerbaijan':'Asia','Turkmenistan':'Asia','Bahrain':'Asia','Singapore':'Asia','Israel':'Asia','Jordan':'Asia','Yemen':'Asia','Oman':'Asia','South Africa':'Africa','Nigeria':'Africa','Egypt':'Africa','Algeria':'Africa','Morocco':'Africa','Angola':'Africa','Kenya':'Africa','Ethiopia':'Africa','Ghana':'Africa','Tanzania':'Africa','Sudan':'Africa','Libya':'Africa','Tunisia':'Africa','Cameroon':'Africa','Ivory Coast':'Africa','Zimbabwe':'Africa','Zambia':'Africa','Uganda':'Africa','Mozambique':'Africa','Senegal':'Africa','Australia':'Oceania','New Zealand':'Oceania'};
  const countryTimeSeries={};
  countries.forEach(c=>{
    const rng=seed(c.split('').reduce((a,b)=>a+b.charCodeAt(0),0));
    const base=BASE_CO2[c]||rand(20,500);
    const growth=GROWTH[c]!==undefined?GROWTH[c]:rand(-0.02,0.05);
    const series={years:[],co2:[],pc:[]};
    let prev=base*Math.pow(1+growth,-33);
    years.forEach((yr,i)=>{
      const noise=1+(rng()-0.5)*0.12;
      const val=Math.max(0.1,prev*(1+growth)*noise);
      prev=val;
      const pop=rand(50000,2000000)*(1+rand(0.005,0.02))**i;
      const pc=(val*1e6)/(pop*1000/1000);
      series.years.push(yr);series.co2.push(val);series.pc.push(Math.min(pc,60));
      raceData[i].Data.push({Country:c,CO2_mt:val,CO2_per_capita:pc});
      mapData.push({Country:c,Year:yr,CO2_mt:val,CO2_per_capita:Math.min(pc,60)});
      const region=regionMap[c]||'Other';
      if(!sankeyData[i].Regions[region]) sankeyData[i].Regions[region]=0;
      sankeyData[i].Regions[region]+=val;
    });
    countryTimeSeries[c]=series;
    compData.push({Country:c,Years:series.years,CO2:series.co2,PerCapita:series.pc,First_Year:series.years[0],Last_Year:series.years.at(-1),First_CO2:series.co2[0],Last_CO2:series.co2.at(-1),CO2_Change:series.co2.at(-1)-series.co2[0],CO2_Pct_Change:((series.co2.at(-1)-series.co2[0])/series.co2[0]*100),First_Per_Capita:series.pc[0],Last_Per_Capita:series.pc.at(-1),Per_Capita_Change:series.pc.at(-1)-series.pc[0],Per_Capita_Pct_Change:((series.pc.at(-1)-series.pc[0])/series.pc[0]*100)});
  });
  countries.forEach(c=>{
    const s=countryTimeSeries[c];
    s.years.slice(1).forEach((yr,i)=>{
      const yIdx=years.indexOf(yr)-1;
      if(yIdx<0) return;
      const prev=s.co2[i],curr=s.co2[i+1];
      const gr=prev>0?(curr-prev)/prev*100:0;
      growthRaceData[yIdx].Data.push({Country:c,Growth_Rate:gr,CO2_mt:curr});
    });
  });
  raceData.forEach((frame,i)=>{
    frame.Data.sort((a,b)=>b.CO2_mt-a.CO2_mt);
    sankeyData[i].TopEmitters=frame.Data.slice(0,15).map(d=>({Country:d.Country,CO2_mt:d.CO2_mt}));
  });
  const yearlyTotals=years.map((yr,i)=>{const s=raceData[i].Data.reduce((a,d)=>a+d.CO2_mt,0);return{Year:yr,Total_CO2:s,Per_Capita:s/countries.length};});
  window.DATA={compData,mapData,raceData,growthRaceData,sankeyData,yearlyTotals,regionMap,globalStats:{peak_year:yearlyTotals.reduce((a,b)=>b.Total_CO2>a.Total_CO2?b:a).Year,total_countries:countries.length}};
})();

/* ════ COLOR PALETTE ════ */
const MASTER_PALETTE=['#ff5f2e','#f5c842','#2edfb4','#9b7ff4','#f06bac','#38c4f5','#fb9c3a','#34dba8','#7c9cf8','#f478c5','#e8f542','#42f5a7','#f54278','#42c8f5','#f5a142','#c842f5','#42f578','#f54242','#4278f5','#f5e642','#8bf542','#f542c8','#42f5f5','#f57842','#a2f542','#f542a2','#42d4f5','#f5c242','#6af542','#d442f5','#f57842','#42f5a2','#f54278','#78f542','#f5428a'];
const countryColorMap={};
(function(){window.ALL_COUNTRIES.forEach((c,i)=>{countryColorMap[c]=MASTER_PALETTE[i%MASTER_PALETTE.length];});})();
function getCC(c){return countryColorMap[c]||'#8a96b3';}

/* ════ PLOTLY THEME ════ */
function getDarkLayout(){
  const d=document.documentElement.getAttribute('data-theme')==='dark';
  return{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{family:"'DM Sans',sans-serif",color:d?'#e4e9f4':'#1a2040',size:12},xaxis:{gridcolor:d?'rgba(255,255,255,0.055)':'rgba(0,0,0,0.06)',zerolinecolor:d?'rgba(255,255,255,0.09)':'rgba(0,0,0,0.1)'},yaxis:{gridcolor:d?'rgba(255,255,255,0.055)':'rgba(0,0,0,0.06)',zerolinecolor:d?'rgba(255,255,255,0.09)':'rgba(0,0,0,0.1)'},margin:{l:160,r:60,t:60,b:50}};
}
const PC={responsive:true,displayModeBar:false};

/* ════ THEME TOGGLE ════ */
function toggleTheme(){
  const h=document.documentElement,d=h.getAttribute('data-theme')==='dark';
  h.setAttribute('data-theme',d?'light':'dark');
  document.getElementById('themeToggleBtn').textContent=d?'🌙':'☀️';
  const a=document.querySelector('.tab-content.active')?.id;
  if(a) redrawTab(a);
}
function redrawTab(n){
  if(n==='worldmap') updateMapDisplay();
  if(n==='animation'){raceInitialized=false;drawRaceFrame(raceFrameIdx);}
  if(n==='growthrace'){growthInitialized=false;drawGrowthFrame(growthFrameIdx);}
  if(n==='compare') updateCompare();
  if(n==='trends') updateTrend();
  if(n==='heatmap') updateHeat();
  if(n==='sankey') updateSankey();
  if(n==='rankings') updateRankings();
  if(n==='glance') renderGlance();
  if(n==='footprint') renderFootprint();
}

/* ════ TAB SWITCH ════ */
function switchTab(name){
  stopAllTimers();hideTooltip();
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById(name).classList.add('active');
  document.querySelectorAll('.tab-btn').forEach(b=>{if(b.getAttribute('onclick')?.includes("'"+name+"'")) b.classList.add('active');});
  setTimeout(()=>redrawTab(name),50);
}

/* ════ INIT ════ */
function init(){
  populateDropdowns();updateKPIs();setupRaceSlider();setupGrowthSlider();setupSankeySlider();
  updateMapDisplay();updateRankings();updateTrend();populateDataTable();updateCompare();updateHeat();updateSankey();
}
function updateKPIs(){
  const D=window.DATA,l=D.yearlyTotals.at(-1);
  document.getElementById('kpi1').textContent=Math.round(l.Total_CO2).toLocaleString();
  document.getElementById('kpi2').textContent=D.globalStats.total_countries;
  document.getElementById('kpi3').textContent=window.ALL_YEARS[0]+'–'+window.ALL_YEARS.at(-1);
  document.getElementById('kpi4').textContent=D.globalStats.peak_year;
}
function populateDropdowns(){
  const yrs=window.ALL_YEARS,cts=[...window.DATA.compData].map(d=>d.Country).sort();
  ['mapYearSelect','sankeyYrSel','heatFrom','heatTo'].forEach(id=>{
    const el=document.getElementById(id);
    yrs.forEach(y=>{el.innerHTML+=`<option value="${y}">${y}</option>`;});
    el.value=yrs.at(-1);
  });
  document.getElementById('heatFrom').value=yrs[0];
  ['c1Sel','c2Sel','trendSel','heatSel'].forEach(id=>{
    const el=document.getElementById(id);
    cts.forEach(c=>{el.innerHTML+=`<option value="${c}">${c}</option>`;});
  });
  if(cts.length>1) document.getElementById('c2Sel').value=cts[1];
}

/* ════════════════════════════════════════
   SHARED RICH TOOLTIP ENGINE
════════════════════════════════════════ */
let _ttMX=0,_ttMY=0;
document.addEventListener('mousemove',e=>{_ttMX=e.clientX;_ttMY=e.clientY;});

function hideTooltip(){document.getElementById('richTooltip').classList.remove('visible');}

function buildSparklineHTML(co2series,col){
  if(!co2series||co2series.length<2) return '';
  const vs=co2series,mn=Math.min(...vs),mx=Math.max(...vs),rng=mx-mn||1;
  const W=160,H=36,p=2;
  const pts=vs.map((v,j)=>`${p+(j/(vs.length-1))*(W-p*2)},${H-p-(v-mn)/rng*(H-p*2)}`);
  const lx=pts[pts.length-1].split(',')[0],ly=H-p,fx=pts[0].split(',')[0];
  return `<polyline points="${pts.join(' ')}" fill="none" stroke="${col}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
    <polygon points="${fx},${ly} ${pts.join(' ')} ${lx},${ly}" fill="${col}" opacity="0.15"/>
    <circle cx="${lx}" cy="${pts[pts.length-1].split(',')[1]}" r="3" fill="${col}"/>`;
}

function showCountryTooltip(country, yr, footerText){
  const tt=document.getElementById('richTooltip');
  const yrVal=yr||window.ALL_YEARS.at(-1);
  const yrData=window.DATA.mapData.filter(d=>d.Year===yrVal);
  const entry=yrData.find(d=>d.Country===country);
  const col=getCC(country);
  const region=window.DATA.regionMap[country]||'Other';
  const sorted=[...yrData].sort((a,b)=>b.CO2_mt-a.CO2_mt);
  const rank=entry?sorted.findIndex(d=>d.Country===country)+1:0;
  const totalCO2=sorted.reduce((s,d)=>s+d.CO2_mt,0);
  const co2val=entry?entry.CO2_mt:0;
  const pcval=entry?entry.CO2_per_capita:0;
  const share=entry?(co2val/totalCO2*100):0;

  // YoY
  const prevData=window.DATA.mapData.filter(d=>d.Year===yrVal-1);
  const prevEntry=prevData.find(d=>d.Country===country);
  let yoyHtml='<span style="color:var(--text2)">No prior data</span>';
  if(prevEntry&&entry){
    const delta=entry.CO2_mt-prevEntry.CO2_mt,pct=(delta/prevEntry.CO2_mt*100);
    const c=delta>0?'var(--a1)':'var(--a3)',ar=delta>0?'↑':'↓';
    yoyHtml=`<span style="color:${c};font-family:'Syne',sans-serif;font-weight:700">${ar} ${Math.abs(pct).toFixed(1)}%</span>`;
  }

  // Sparkline + trend
  const cmp=window.DATA.compData.find(d=>d.Country===country);
  let sparkHtml='',trendDirHtml='—',trendPctHtml='since 1990';
  if(cmp){
    sparkHtml=buildSparklineHTML(cmp.CO2,col);
    const rising=cmp.CO2_Pct_Change>0;
    trendDirHtml=`<span style="color:${rising?'var(--a1)':'var(--a3)'}">${rising?'↑ Rising':'↓ Falling'}</span>`;
    trendPctHtml=`${rising?'+':''}${cmp.CO2_Pct_Change.toFixed(1)}% since ${cmp.First_Year}`;
  }

  document.getElementById('ttCountry').innerHTML=`<span class="tt-color-dot" style="background:${col}"></span>${country}`;
  document.getElementById('ttRegion').textContent=region;
  document.getElementById('ttRankNum').textContent=rank?'#'+rank:'—';
  document.getElementById('ttCO2').textContent=co2val>=1000?(co2val/1000).toFixed(2)+' Gt':co2val.toFixed(1)+' Mt';
  document.getElementById('ttPC').textContent=pcval.toFixed(2)+' t/person';
  document.getElementById('ttShare').textContent=share.toFixed(2)+'%';
  document.getElementById('ttRegionVal').textContent=region;
  document.getElementById('ttYoY').innerHTML=yoyHtml;
  document.getElementById('ttSparkline').innerHTML=sparkHtml;
  document.getElementById('ttTrendDir').innerHTML=trendDirHtml;
  document.getElementById('ttTrendPct').textContent=trendPctHtml;
  document.getElementById('ttFooter').textContent=footerText||'Click to open trend analysis →';

  positionTooltip();
  tt.classList.add('visible');
}

function positionTooltip(){
  const tt=document.getElementById('richTooltip');
  const TW=310,TH=270;
  let tx=_ttMX+18,ty=_ttMY-TH/2;
  if(tx+TW>window.innerWidth-10) tx=_ttMX-TW-18;
  if(ty<10) ty=10;
  if(ty+TH>window.innerHeight-10) ty=window.innerHeight-TH-10;
  tt.style.left=tx+'px';tt.style.top=ty+'px';
}

/* ════════════════════════════════════════
   WORLD MAP
════════════════════════════════════════ */
let mapMode='choropleth',mapMetric='co2',mapYearIdx=0,mapTimer=null,mapSpeed=1000;

function setMapMode(m){mapMode=m;document.getElementById('modeChoro').classList.toggle('active',m==='choropleth');document.getElementById('modeBubble').classList.toggle('active',m==='bubble');updateMapDisplay();}
function setMapMetric(m){mapMetric=m;document.getElementById('metricCO2').classList.toggle('active',m==='co2');document.getElementById('metricPC').classList.toggle('active',m==='per_capita');updateMapDisplay();}
function setMapSpeed(s){mapSpeed=s;document.querySelectorAll('.map-speed-btn').forEach((b,i)=>{b.classList.toggle('active',[2000,1000,500,250][i]===s);});if(mapTimer){clearInterval(mapTimer);mapTimer=setInterval(mapAutoStep,mapSpeed);}}
function jumpMapYear(yr){mapYearIdx=Math.max(0,window.ALL_YEARS.indexOf(+yr));updateMapDisplay();}
function mapPrevYear(){mapYearIdx=Math.max(0,mapYearIdx-1);updateMapDisplay();document.getElementById('mapYearSelect').value=window.ALL_YEARS[mapYearIdx];}
function mapNextYear(){mapYearIdx=Math.min(window.ALL_YEARS.length-1,mapYearIdx+1);updateMapDisplay();document.getElementById('mapYearSelect').value=window.ALL_YEARS[mapYearIdx];}
function toggleMapPlay(){if(mapTimer){clearInterval(mapTimer);mapTimer=null;document.getElementById('mapPlayBtn').textContent='▶';}else{document.getElementById('mapPlayBtn').textContent='⏸';mapTimer=setInterval(mapAutoStep,mapSpeed);}}
function mapAutoStep(){mapYearIdx++;if(mapYearIdx>=window.ALL_YEARS.length)mapYearIdx=0;document.getElementById('mapYearSelect').value=window.ALL_YEARS[mapYearIdx];updateMapDisplay();}

function updateMapDisplay(){
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const yr=window.ALL_YEARS[mapYearIdx];
  document.getElementById('mapYearNum').textContent=yr;
  document.getElementById('mapProgressBar').style.width=Math.round((mapYearIdx/(window.ALL_YEARS.length-1))*100)+'%';
  document.getElementById('mapYearSelect').value=yr;
  const yrData=window.DATA.mapData.filter(d=>d.Year===yr);
  const vals=yrData.map(d=>mapMetric==='co2'?d.CO2_mt:d.CO2_per_capita);
  const textColor=isDark?'#e4e9f4':'#1a2040';
  const fontConfig={family:"'DM Sans',sans-serif",color:textColor,size:11};
  const colorscaleCO2=isDark?[[0,'#0d1117'],[0.15,'#4a1531'],[0.35,'#9d1f45'],[0.6,'#e05025'],[0.85,'#f5a742'],[1,'#fde888']]:[[0,'#fff5f0'],[0.2,'#ffc2a4'],[0.45,'#ff7848'],[0.7,'#d43a15'],[0.9,'#8b1500'],[1,'#4a0800']];
  const colorscalePC=isDark?[[0,'#051c1a'],[0.25,'#0a5f56'],[0.5,'#1da892'],[0.75,'#6dd5c4'],[1,'#c4f5ee']]:[[0,'#f0fffe'],[0.25,'#a0e8e0'],[0.5,'#40c8b8'],[0.75,'#158070'],[1,'#043530']];
  const geoBase={bgcolor:'rgba(0,0,0,0)',showframe:false,showcoastlines:true,coastlinecolor:isDark?'rgba(255,255,255,0.12)':'rgba(0,0,0,0.18)',projection:{type:'natural earth'},showland:true,landcolor:isDark?'#1e2740':'#dde3f5',showocean:true,oceancolor:isDark?'#0a0e1a':'#c8d4ef',showcountries:true,countrycolor:isDark?'rgba(255,255,255,0.07)':'rgba(0,0,0,0.09)'};
  const baseLayout={paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:fontConfig,title:{text:`<b>Carbon Emissions — ${yr}</b>`,font:{size:18,color:textColor},x:.5},margin:{l:0,r:0,t:54,b:0},geo:geoBase,hoverlabel:{bgcolor:'rgba(0,0,0,0)',bordercolor:'rgba(0,0,0,0)',font:{size:1,color:'rgba(0,0,0,0)'}}};

  if(mapMode==='choropleth'){
    Plotly.newPlot('worldMapChart',[{type:'choropleth',locationmode:'country names',locations:yrData.map(d=>d.Country),z:vals,customdata:yrData.map(d=>d.Country),colorscale:mapMetric==='co2'?colorscaleCO2:colorscalePC,colorbar:{title:{text:mapMetric==='co2'?'Mt CO₂':'t/person',side:'right'},tickfont:fontConfig,titlefont:fontConfig},marker:{line:{color:isDark?'rgba(255,255,255,0.07)':'rgba(0,0,0,0.1)',width:0.6}},hovertemplate:' <extra></extra>'}],baseLayout,PC);
  } else {
    const sorted=[...yrData].sort((a,b)=>b.CO2_mt-a.CO2_mt).slice(0,80);
    Plotly.newPlot('worldMapChart',[{type:'scattergeo',mode:'markers',locations:sorted.map(d=>d.Country),locationmode:'country names',customdata:sorted.map(d=>d.Country),marker:{size:sorted.map(d=>Math.max(7,Math.sqrt(mapMetric==='co2'?d.CO2_mt:d.CO2_per_capita*50)*2.4)),color:sorted.map(d=>getCC(d.Country)),opacity:0.82,line:{color:isDark?'rgba(255,255,255,0.25)':'rgba(0,0,0,0.25)',width:1.5},sizemode:'area'},hovertemplate:' <extra></extra>'},{type:'choropleth',locationmode:'country names',locations:yrData.map(d=>d.Country),z:yrData.map(()=>0),colorscale:[[0,isDark?'#1e2740':'#dde3f5'],[1,isDark?'#1e2740':'#dde3f5']],showscale:false,marker:{line:{color:isDark?'rgba(255,255,255,0.06)':'rgba(0,0,0,0.09)',width:0.5}},hoverinfo:'skip'}],baseLayout,PC);
  }

  const mapEl=document.getElementById('worldMapChart');
  mapEl.on('plotly_hover',function(data){
    const pt=data.points?.[0];if(!pt) return;
    const country=pt.customdata||pt.location;if(!country) return;
    showCountryTooltip(country,yr,'Click to open trend analysis →');
  });
  mapEl.on('plotly_unhover',hideTooltip);
  mapEl.on('plotly_click',function(data){
    const pt=data.points?.[0];
    const country=pt?.customdata||pt?.location;if(!country) return;
    hideTooltip();switchTab('trends');
    const s=document.getElementById('trendSel');
    if([...s.options].some(o=>o.value===country)){s.value=country;updateTrend();}
  });
}

/* ════════════════════════════════════════
   EMISSION RACE — ALL COUNTRIES
════════════════════════════════════════ */
let raceTimer=null,raceFrameIdx=0,raceInitialized=false;
const RACE_MAX_CO2=(function(){let m=0;window.DATA.raceData.forEach(f=>f.Data.forEach(d=>{if(d.CO2_mt>m)m=d.CO2_mt;}));return m*1.25;})();

function setupRaceSlider(){
  const s=document.getElementById('raceSlider');
  s.max=window.DATA.raceData.length-1;s.value=0;
  raceFrameIdx=0;raceInitialized=false;drawRaceFrame(0);
}

function drawRaceFrame(idx){
  raceFrameIdx=idx;
  document.getElementById('raceSlider').value=idx;
  const frame=window.DATA.raceData[idx];if(!frame) return;
  const topN=+document.getElementById('raceTopN').value;
  const sorted=[...frame.Data].sort((a,b)=>a.CO2_mt-b.CO2_mt).slice(-topN);
  document.getElementById('raceYearDisp').textContent=frame.Year;
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const textColor=isDark?'#8a96b3':'#5a6480',titleColor=isDark?'#e4e9f4':'#1a2040';
  const chartH=Math.max(500,sorted.length*28);
  document.getElementById('raceChart').style.height=chartH+'px';

  const trace=[{x:sorted.map(d=>d.CO2_mt),y:sorted.map(d=>d.Country),type:'bar',orientation:'h',marker:{color:sorted.map(d=>getCC(d.Country)),opacity:.88,line:{color:'rgba(0,0,0,0.25)',width:1}},text:sorted.map(d=>d.CO2_mt.toFixed(1)+' Mt'),textposition:'outside',textfont:{color:textColor,size:10},customdata:sorted.map(d=>d.Country),hovertemplate:' <extra></extra>'}];
  const layout={...getDarkLayout(),title:{text:`<b>CO₂ Emitters — ${frame.Year}</b>`,font:{size:17,color:titleColor},x:.5},xaxis:{...getDarkLayout().xaxis,title:'Million Tonnes CO₂',range:[0,RACE_MAX_CO2],fixedrange:true},yaxis:{...getDarkLayout().yaxis,automargin:true,fixedrange:true},height:chartH,transition:{duration:180,easing:'cubic-in-out'}};

  if(!raceInitialized){Plotly.newPlot('raceChart',trace,layout,PC);raceInitialized=true;
    const el=document.getElementById('raceChart');
    el.on('plotly_hover',function(data){const pt=data.points?.[0];if(!pt) return;showCountryTooltip(pt.customdata,frame.Year,'Click to open trend →');});
    el.on('plotly_unhover',hideTooltip);
    el.on('plotly_click',function(data){const pt=data.points?.[0];if(!pt) return;hideTooltip();switchTab('trends');const s=document.getElementById('trendSel');if([...s.options].some(o=>o.value===pt.customdata)){s.value=pt.customdata;updateTrend();}});
  } else {Plotly.react('raceChart',trace,layout,PC);}
}
function jumpRaceFrame(idx){drawRaceFrame(+idx);}
function toggleRace(){
  if(raceTimer){clearInterval(raceTimer);raceTimer=null;document.getElementById('racePlayBtn').textContent='▶ Play Race';return;}
  if(raceFrameIdx>=window.DATA.raceData.length-1) raceFrameIdx=0;
  document.getElementById('racePlayBtn').textContent='⏸ Pause';
  raceTimer=setInterval(function(){drawRaceFrame(raceFrameIdx);raceFrameIdx++;if(raceFrameIdx>=window.DATA.raceData.length){clearInterval(raceTimer);raceTimer=null;document.getElementById('racePlayBtn').textContent='▶ Play Race';}},+document.getElementById('raceSpeed').value);
}
function resetRace(){if(raceTimer){clearInterval(raceTimer);raceTimer=null;}document.getElementById('racePlayBtn').textContent='▶ Play Race';raceFrameIdx=0;raceInitialized=false;drawRaceFrame(0);}

/* ════════════════════════════════════════
   GROWTH RACE — ALL COUNTRIES
════════════════════════════════════════ */
let growthTimer=null,growthFrameIdx=0,growthInitialized=false;
const GROWTH_RANGE=(function(){let mn=0,mx=0;window.DATA.growthRaceData.forEach(f=>f.Data.forEach(d=>{if(d.Growth_Rate>mx)mx=d.Growth_Rate;if(d.Growth_Rate<mn)mn=d.Growth_Rate;}));return[mn*1.2,mx*1.2];})();

function setupGrowthSlider(){
  const s=document.getElementById('growthSlider');
  s.max=window.DATA.growthRaceData.length-1;s.value=0;
  growthFrameIdx=0;growthInitialized=false;drawGrowthFrame(0);
}

function drawGrowthFrame(idx){
  growthFrameIdx=idx;
  document.getElementById('growthSlider').value=idx;
  const frame=window.DATA.growthRaceData[idx];if(!frame) return;
  const topN=+document.getElementById('growthTopN').value;
  const sorted=[...frame.Data].sort((a,b)=>a.Growth_Rate-b.Growth_Rate).slice(-topN);
  document.getElementById('growthYearDisp').textContent=frame.Year;
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const textColor=isDark?'#8a96b3':'#5a6480',titleColor=isDark?'#e4e9f4':'#1a2040';
  const chartH=Math.max(500,sorted.length*28);
  document.getElementById('growthRaceChart').style.height=chartH+'px';

  const trace=[{x:sorted.map(d=>d.Growth_Rate),y:sorted.map(d=>d.Country),type:'bar',orientation:'h',marker:{color:sorted.map(d=>getCC(d.Country)),opacity:.88,line:{color:'rgba(0,0,0,0.25)',width:1}},text:sorted.map(d=>(d.Growth_Rate>=0?'+':'')+d.Growth_Rate.toFixed(1)+'%'),textposition:'outside',textfont:{color:textColor,size:10},customdata:sorted.map(d=>d.Country),hovertemplate:' <extra></extra>'}];
  const layout={...getDarkLayout(),title:{text:`<b>Fastest Growing Emissions — ${frame.Year}</b>`,font:{size:17,color:titleColor},x:.5},xaxis:{...getDarkLayout().xaxis,title:'Year-on-Year Growth Rate (%)',range:GROWTH_RANGE,fixedrange:true},yaxis:{...getDarkLayout().yaxis,automargin:true,fixedrange:true},height:chartH,transition:{duration:180,easing:'cubic-in-out'}};

  if(!growthInitialized){Plotly.newPlot('growthRaceChart',trace,layout,PC);growthInitialized=true;
    const el=document.getElementById('growthRaceChart');
    el.on('plotly_hover',function(data){const pt=data.points?.[0];if(!pt) return;showCountryTooltip(pt.customdata,frame.Year,'Click to open trend →');});
    el.on('plotly_unhover',hideTooltip);
    el.on('plotly_click',function(data){const pt=data.points?.[0];if(!pt) return;hideTooltip();switchTab('trends');const s=document.getElementById('trendSel');if([...s.options].some(o=>o.value===pt.customdata)){s.value=pt.customdata;updateTrend();}});
  } else {Plotly.react('growthRaceChart',trace,layout,PC);}
}
function jumpGrowthFrame(idx){drawGrowthFrame(+idx);}
function toggleGrowthRace(){
  if(growthTimer){clearInterval(growthTimer);growthTimer=null;document.getElementById('growthPlayBtn').textContent='▶ Play Race';return;}
  if(growthFrameIdx>=window.DATA.growthRaceData.length-1) growthFrameIdx=0;
  document.getElementById('growthPlayBtn').textContent='⏸ Pause';
  growthTimer=setInterval(function(){drawGrowthFrame(growthFrameIdx);growthFrameIdx++;if(growthFrameIdx>=window.DATA.growthRaceData.length){clearInterval(growthTimer);growthTimer=null;document.getElementById('growthPlayBtn').textContent='▶ Play Race';}},+document.getElementById('growthSpeed').value);
}
function resetGrowthRace(){if(growthTimer){clearInterval(growthTimer);growthTimer=null;}document.getElementById('growthPlayBtn').textContent='▶ Play Race';growthFrameIdx=0;growthInitialized=false;drawGrowthFrame(0);}

/* ════ STOP ALL TIMERS ════ */
function stopAllTimers(){
  if(raceTimer){clearInterval(raceTimer);raceTimer=null;}
  if(growthTimer){clearInterval(growthTimer);growthTimer=null;}
  if(mapTimer){clearInterval(mapTimer);mapTimer=null;}
  if(fpTimer){clearInterval(fpTimer);fpTimer=null;}
  document.getElementById('racePlayBtn').textContent='▶ Play Race';
  document.getElementById('growthPlayBtn').textContent='▶ Play Race';
  document.getElementById('mapPlayBtn').textContent='▶';
  const fpBtn=document.getElementById('fpPlayBtn');if(fpBtn) fpBtn.textContent='▶ Animate';
}

/* ════════════════════════════════════════
   COMPARE — with rich hover tooltip
════════════════════════════════════════ */
function updateCompare(){
  const c1=document.getElementById('c1Sel').value,c2=document.getElementById('c2Sel').value;
  const d1=window.DATA.compData.find(d=>d.Country===c1),d2=window.DATA.compData.find(d=>d.Country===c2);
  if(!d1||!d2) return;
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const col1=getCC(c1),col2=getCC(c2);

  Plotly.newPlot('compareChart',[
    {x:d1.Years,y:d1.CO2,type:'scatter',mode:'lines+markers',name:c1,line:{color:col1,width:3},marker:{size:7,color:col1,line:{color:'rgba(0,0,0,0.3)',width:1.5}},customdata:d1.Years.map(()=>c1),hovertemplate:' <extra></extra>'},
    {x:d2.Years,y:d2.CO2,type:'scatter',mode:'lines+markers',name:c2,line:{color:col2,width:3},marker:{size:7,color:col2,line:{color:'rgba(0,0,0,0.3)',width:1.5}},customdata:d2.Years.map(()=>c2),hovertemplate:' <extra></extra>'}
  ],{
    ...getDarkLayout(),
    title:{text:`<b>${c1}</b> vs <b>${c2}</b> — CO₂ Emissions`,font:{size:17,color:isDark?'#e4e9f4':'#1a2040'},x:.5},
    xaxis:{...getDarkLayout().xaxis,title:'Year'},
    yaxis:{...getDarkLayout().yaxis,title:'Million Tonnes CO₂'},
    hovermode:'closest',
    legend:{bgcolor:'rgba(0,0,0,0)',bordercolor:isDark?'rgba(255,255,255,.1)':'rgba(0,0,0,.1)',borderwidth:1}
  },PC);

  const cmpEl=document.getElementById('compareChart');
  cmpEl.on('plotly_hover',function(data){
    const pt=data.points?.[0];if(!pt) return;
    const country=pt.customdata;const yr=pt.x;
    showCountryTooltip(country,yr,'Country emissions profile');
  });
  cmpEl.on('plotly_unhover',hideTooltip);
  cmpEl.on('plotly_click',function(data){
    const pt=data.points?.[0];if(!pt) return;
    const country=pt.customdata;hideTooltip();
    switchTab('trends');
    const s=document.getElementById('trendSel');
    if([...s.options].some(o=>o.value===country)){s.value=country;updateTrend();}
  });

  const statsEl=document.getElementById('compareStats');
  statsEl.style.display='block';
  const sg=v=>(v>0?'+':'')+v.toFixed(1);
  const c=v=>v>0?'up':'dn';
  statsEl.innerHTML=`<h3>Detailed Comparison — ${c1} vs ${c2}</h3><div class="cmp-grid">
    <div class="cmp-m"><div class="cv ${c(d1.CO2_Change)}">${sg(d1.CO2_Change)} Mt</div><div class="cl">${c1} — CO₂ Change</div></div>
    <div class="cmp-m"><div class="cv ${c(d2.CO2_Change)}">${sg(d2.CO2_Change)} Mt</div><div class="cl">${c2} — CO₂ Change</div></div>
    <div class="cmp-m"><div class="cv ${c(d1.CO2_Pct_Change)}">${sg(d1.CO2_Pct_Change)}%</div><div class="cl">${c1} — Growth Rate</div></div>
    <div class="cmp-m"><div class="cv ${c(d2.CO2_Pct_Change)}">${sg(d2.CO2_Pct_Change)}%</div><div class="cl">${c2} — Growth Rate</div></div>
    <div class="cmp-m"><div class="cv">${d1.Last_Per_Capita.toFixed(2)} t</div><div class="cl">${c1} — Latest Per Capita</div></div>
    <div class="cmp-m"><div class="cv">${d2.Last_Per_Capita.toFixed(2)} t</div><div class="cl">${c2} — Latest Per Capita</div></div>
  </div>`;
}

/* ════════════════════════════════════════
   TREND ANALYSIS — with rich hover tooltip
════════════════════════════════════════ */
function updateTrend(){
  const country=document.getElementById('trendSel').value;
  const d=window.DATA.compData.find(x=>x.Country===country);if(!d) return;
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const col=getCC(country);
  const n=d.Years.length,sx=d.Years.reduce((a,b)=>a+b,0),sy=d.CO2.reduce((a,b)=>a+b,0);
  const sxy=d.Years.reduce((s,x,i)=>s+x*d.CO2[i],0),sx2=d.Years.reduce((s,x)=>s+x*x,0);
  const slope=(n*sxy-sx*sy)/(n*sx2-sx*sx),int=(sy-slope*sx)/n;
  const trend=d.Years.map(x=>slope*x+int);
  const ma=d.CO2.map((_,i)=>i===0||i===d.CO2.length-1?d.CO2[i]:(d.CO2[i-1]+d.CO2[i]+d.CO2[i+1])/3);

  const fillCol=col+'28';
  Plotly.newPlot('trendChart',[
    {x:d.Years,y:d.CO2,type:'scatter',mode:'lines+markers',name:'Actual',line:{color:col,width:2.5},marker:{size:6,color:col,line:{color:'rgba(0,0,0,0.35)',width:1}},fill:'tozeroy',fillcolor:fillCol,customdata:d.Years.map(()=>country),hovertemplate:' <extra></extra>'},
    {x:d.Years,y:trend,type:'scatter',mode:'lines',name:'Trend',line:{color:'#ff5f2e',width:2,dash:'dash'},hovertemplate:'Trend: %{y:.1f} Mt<extra></extra>'},
    {x:d.Years,y:ma,type:'scatter',mode:'lines',name:'3-yr MA',line:{color:'#2edfb4',width:2},hovertemplate:'3yr MA: %{y:.1f} Mt<extra></extra>'}
  ],{
    ...getDarkLayout(),
    title:{text:`<b>${country}</b> — Trend Analysis`,font:{size:17,color:isDark?'#e4e9f4':'#1a2040'},x:.5},
    xaxis:{...getDarkLayout().xaxis,title:'Year'},
    yaxis:{...getDarkLayout().yaxis,title:'Million Tonnes CO₂'},
    hovermode:'x unified',
    legend:{bgcolor:'rgba(0,0,0,0)',bordercolor:isDark?'rgba(255,255,255,.1)':'rgba(0,0,0,.1)',borderwidth:1}
  },PC);

  const tEl=document.getElementById('trendChart');
  tEl.on('plotly_hover',function(data){
    const pt=data.points?.[0];if(!pt) return;
    const yr=pt.x;showCountryTooltip(country,yr,'Emissions in '+yr);
  });
  tEl.on('plotly_unhover',hideTooltip);

  const sg=v=>(v>0?'+':'')+v.toFixed(1);
  document.getElementById('trendStats').innerHTML=`
    <div class="mc c1"><div class="ml">CO₂ Change (${d.First_Year}–${d.Last_Year})</div><div class="mv ${d.CO2_Change>0?'up':'dn'}">${sg(d.CO2_Change)} Mt</div></div>
    <div class="mc c2"><div class="ml">Overall Change %</div><div class="mv ${d.CO2_Pct_Change>0?'up':'dn'}">${sg(d.CO2_Pct_Change)}%</div></div>
    <div class="mc c3"><div class="ml">Trend Direction</div><div class="mv" style="font-size:1.2rem">${slope>0?'↑ Rising':'↓ Falling'}</div></div>
    <div class="mc c4"><div class="ml">Latest Per Capita</div><div class="mv">${d.Last_Per_Capita.toFixed(2)} t</div></div>`;
}

/* ════ HEAT CALENDAR ════ */
function updateHeat(){
  const country=document.getElementById('heatSel').value;
  const y0=+document.getElementById('heatFrom').value,y1=+document.getElementById('heatTo').value;
  const d=window.DATA.compData.find(x=>x.Country===country);if(!d) return;
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const yrs=d.Years.filter(y=>y>=y0&&y<=y1);
  const vals=d.CO2.filter((_,i)=>d.Years[i]>=y0&&d.Years[i]<=y1);
  Plotly.newPlot('heatChart',[{z:yrs.map(()=>vals),x:yrs,y:yrs,type:'heatmap',colorscale:isDark?[[0,'#051c1a'],[0.25,'#065f56'],[0.5,'#f59e0b'],[0.75,'#dc2626'],[1,'#fde68a']]:[[0,'#e0f5f4'],[0.25,'#5dd0c5'],[0.5,'#e09010'],[0.75,'#c02020'],[1,'#7a0000']],showscale:true,colorbar:{title:{text:'CO₂ (Mt)',side:'right'},tickfont:{color:isDark?'#8a96b3':'#5a6480'},titlefont:{color:isDark?'#8a96b3':'#5a6480'}},hovertemplate:'Year: %{x}<br>Emissions: %{z:.1f} Mt<extra></extra>'}],{...getDarkLayout(),title:{text:`<b>${country}</b> — Emissions Heat Calendar`,font:{size:17,color:isDark?'#e4e9f4':'#1a2040'},x:.5},xaxis:{...getDarkLayout().xaxis,title:'Year',tickangle:-45},yaxis:{...getDarkLayout().yaxis,title:'Year',autorange:'reversed'},margin:{l:80,r:40,t:60,b:80}},PC);
}

/* ════ SANKEY ════ */
function setupSankeySlider(){
  const s=document.getElementById('sankeySlider');
  s.max=window.DATA.sankeyData.length-1;s.value=window.DATA.sankeyData.length-1;
  document.getElementById('sankeyYearDisp').textContent=window.DATA.sankeyData.at(-1).Year;
}
function jumpSankeyFrame(idx){const frame=window.DATA.sankeyData[idx];document.getElementById('sankeyYearDisp').textContent=frame.Year;document.getElementById('sankeyYrSel').value=frame.Year;drawSankey(frame);}
function updateSankey(){const yr=+document.getElementById('sankeyYrSel').value;const frame=window.DATA.sankeyData.find(x=>x.Year===yr);if(!frame) return;const idx=window.DATA.sankeyData.findIndex(x=>x.Year===yr);document.getElementById('sankeySlider').value=idx;document.getElementById('sankeyYearDisp').textContent=yr;drawSankey(frame);}
function drawSankey(frame){
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const regions=Object.keys(frame.Regions),emitters=frame.TopEmitters.slice(0,12);
  const nodes=['Global',...regions,...emitters.map(e=>e.Country)];
  const ni={};nodes.forEach((n,i)=>ni[n]=i);
  const src=[],tgt=[],val=[],lc=[];
  const RC=['#f5c842','#ff5f2e','#2edfb4','#9b7ff4','#f06bac','#38c4f5','#fb9c3a'];
  const nodeColors=['#f5c842',...regions.map((_,i)=>RC[i%RC.length]),...emitters.map(e=>getCC(e.Country))];
  regions.forEach(r=>{const v=frame.Regions[r];if(v>0){src.push(ni['Global']);tgt.push(ni[r]);val.push(v);lc.push('rgba(245,200,66,0.22)');}});
  emitters.forEach(e=>{const r=window.DATA.regionMap[e.Country]||'Other';if(ni[r]!==undefined){src.push(ni[r]);tgt.push(ni[e.Country]);val.push(e.CO2_mt);lc.push('rgba(255,95,46,0.18)');}});
  const textColor=isDark?'#e4e9f4':'#1a2040';
  Plotly.newPlot('sankeyChart',[{type:'sankey',orientation:'h',node:{pad:18,thickness:22,line:{color:isDark?'rgba(255,255,255,0.1)':'rgba(0,0,0,0.1)',width:0.5},label:nodes,color:nodeColors,font:{color:textColor,size:11}},link:{source:src,target:tgt,value:val,color:lc}}],{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',title:{text:`<b>Emissions Flow — ${frame.Year}</b>`,font:{size:17,color:textColor},x:.5},margin:{l:20,r:20,t:60,b:20},font:{color:textColor,size:11}},PC);
}

/* ════════════════════════════════════════
   RANKINGS — ALL COUNTRIES by default + hover tooltip
════════════════════════════════════════ */
function updateRankings(){
  const metric=document.getElementById('rankMetric').value;
  const topN=+document.getElementById('topN').value;
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  let sorted;
  if(metric==='co2') sorted=[...window.DATA.compData].sort((a,b)=>b.Last_CO2-a.Last_CO2);
  else if(metric==='per_capita') sorted=[...window.DATA.compData].sort((a,b)=>b.Last_Per_Capita-a.Last_Per_Capita);
  else sorted=[...window.DATA.compData].sort((a,b)=>b.CO2_Pct_Change-a.CO2_Pct_Change);
  const top=topN>=9999?sorted:sorted.slice(0,topN);
  const vals=top.map(d=>metric==='co2'?d.Last_CO2:metric==='per_capita'?d.Last_Per_Capita:d.CO2_Pct_Change);
  const textColor=isDark?'#e4e9f4':'#1a2040';
  const chartH=Math.max(500,top.length*28);
  document.getElementById('rankChart').style.height=chartH+'px';

  Plotly.newPlot('rankChart',[{x:vals,y:top.map(d=>d.Country),type:'bar',orientation:'h',marker:{color:top.map(d=>getCC(d.Country)),opacity:.88,line:{color:'rgba(0,0,0,0.22)',width:0.8}},text:vals.map(v=>v.toFixed(1)),textposition:'outside',textfont:{color:isDark?'#8a96b3':'#5a6480',size:10},customdata:top.map(d=>d.Country),hovertemplate:' <extra></extra>'}],{
    ...getDarkLayout(),
    title:{text:`<b>${top.length} Countries by ${metric==='co2'?'Total CO₂':metric==='per_capita'?'Per Capita':'Growth Rate'}</b>`,font:{size:16,color:textColor},x:.5},
    xaxis:{...getDarkLayout().xaxis,title:metric==='co2'?'Million Tonnes':metric==='per_capita'?'t/person':'%'},
    yaxis:{...getDarkLayout().yaxis,automargin:true},
    height:chartH,margin:{l:180,r:70,t:60,b:50}
  },PC);

  const rEl=document.getElementById('rankChart');
  rEl.on('plotly_hover',function(data){const pt=data.points?.[0];if(!pt) return;showCountryTooltip(pt.customdata,null,'Click to open trend →');});
  rEl.on('plotly_unhover',hideTooltip);
  rEl.on('plotly_click',function(data){const pt=data.points?.[0];if(!pt) return;hideTooltip();switchTab('trends');const s=document.getElementById('trendSel');if([...s.options].some(o=>o.value===pt.customdata)){s.value=pt.customdata;updateTrend();}});

  document.getElementById('rankStats').innerHTML=`
    <div class="mc c1"><div class="ml">Top Country</div><div class="mv" style="font-size:1rem">${top[0]?.Country||'—'}</div></div>
    <div class="mc c2"><div class="ml">Top Value</div><div class="mv">${vals[0]?.toFixed(1)||'—'}</div></div>
    <div class="mc c3"><div class="ml">Countries Listed</div><div class="mv">${top.length}</div></div>`;
}

/* ════════════════════════════════════════
   DATA TABLE — animated hover description
════════════════════════════════════════ */
function populateDataTable(){
  const tbody=document.getElementById('dataTbody');
  tbody.innerHTML='';
  [...window.DATA.compData].sort((a,b)=>b.Last_CO2-a.Last_CO2).forEach((d,i)=>{
    const up=d.CO2_Pct_Change>0;
    const row=tbody.insertRow();
    const dot=`<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${getCC(d.Country)};margin-right:6px;vertical-align:middle"></span>`;
    row.innerHTML=`
      <td><span class="rank-pill">${i+1}</span></td>
      <td><b>${dot}${d.Country}</b></td>
      <td>${d.First_Year}</td><td>${d.Last_Year}</td>
      <td class="${up?'bu':'bd'}">${up?'+':''}${d.CO2_Change.toFixed(1)}</td>
      <td class="${up?'bu':'bd'}">${up?'+':''}${d.CO2_Pct_Change.toFixed(1)}%</td>
      <td>${d.Per_Capita_Change>0?'+':''}${d.Per_Capita_Change.toFixed(2)}</td>
      <td>${up?'↑ Rising':'↓ Falling'}</td>`;
    // hover: show rich tooltip
    row.addEventListener('mouseenter',function(){
      showCountryTooltip(d.Country,null,'Click to open trend analysis →');
    });
    row.addEventListener('mouseleave',hideTooltip);
    row.onclick=function(){
      hideTooltip();switchTab('trends');
      const s=document.getElementById('trendSel');
      if([...s.options].some(o=>o.value===d.Country)){s.value=d.Country;updateTrend();}
    };
  });
}
function filterTable(){
  const q=document.getElementById('searchInput').value.toLowerCase();
  [...document.getElementById('dataTbody').rows].forEach(r=>{r.style.display=r.textContent.toLowerCase().includes(q)?'':'none';});
}

/* ════ AT A GLANCE ════ */
function renderGlance(){
  const sort=document.getElementById('glanceSortBy').value;
  const region=document.getElementById('glanceRegion').value;
  const metric=document.getElementById('glanceMetric').value;
  const q=(document.getElementById('glanceSearch').value||'').toLowerCase();
  const latestYr=window.ALL_YEARS.at(-1);
  const latestData=window.DATA.mapData.filter(d=>d.Year===latestYr);
  const totalCO2=latestData.reduce((s,d)=>s+d.CO2_mt,0);
  let cards=window.DATA.compData.map(d=>{
    const ld=latestData.find(x=>x.Country===d.Country);
    const co2=ld?ld.CO2_mt:d.Last_CO2,pc=ld?ld.CO2_per_capita:d.Last_Per_Capita;
    const reg=window.DATA.regionMap[d.Country]||'Other';
    return{country:d.Country,co2,pc,reg,change:d.CO2_Pct_Change,co2series:d.CO2,years:d.Years,share:(co2/totalCO2*100)};
  });
  if(region!=='all') cards=cards.filter(c=>c.reg===region);
  if(q) cards=cards.filter(c=>c.country.toLowerCase().includes(q));
  const sorters={co2_desc:(a,b)=>b.co2-a.co2,co2_asc:(a,b)=>a.co2-b.co2,pc_desc:(a,b)=>b.pc-a.pc,pc_asc:(a,b)=>a.pc-b.pc,change_desc:(a,b)=>b.change-a.change,change_asc:(a,b)=>a.change-b.change,alpha:(a,b)=>a.country.localeCompare(b.country)};
  cards.sort(sorters[sort]||sorters.co2_desc);
  const maxCO2=Math.max(...cards.map(c=>c.co2)),maxPC=Math.max(...cards.map(c=>c.pc));
  const total=cards.length,avgPC=(cards.reduce((s,c)=>s+c.pc,0)/total).toFixed(2);
  const risers=cards.filter(c=>c.change>0).length,fallers=cards.filter(c=>c.change<=0).length;
  document.getElementById('glanceSummary').innerHTML=`
    <div class="glance-summary-chip"><div class="gsc-val" style="color:var(--a1)">${total}</div><div class="gsc-lbl">Countries Shown</div></div>
    <div class="glance-summary-chip"><div class="gsc-val" style="color:var(--a3)">${avgPC} t</div><div class="gsc-lbl">Avg Per Capita</div></div>
    <div class="glance-summary-chip"><div class="gsc-val" style="color:var(--a1)">${risers}</div><div class="gsc-lbl">Rising Emissions</div></div>
    <div class="glance-summary-chip"><div class="gsc-val" style="color:var(--a3)">${fallers}</div><div class="gsc-lbl">Falling Emissions</div></div>
    <div class="glance-summary-chip"><div class="gsc-val" style="color:var(--a2)">${cards[0]?.country||'—'}</div><div class="gsc-lbl">#1 by current sort</div></div>`;
  const grid=document.getElementById('glanceGrid');grid.innerHTML='';
  cards.forEach((c,i)=>{
    const col=getCC(c.country);
    const barPct=metric==='co2'?(c.co2/maxCO2*100):metric==='pc'?(c.pc/maxPC*100):Math.max(0,Math.min(100,(c.change+100)/200*100));
    const mainVal=metric==='co2'?(c.co2>=1000?(c.co2/1000).toFixed(2)+' Gt':c.co2.toFixed(1)+' Mt'):metric==='pc'?c.pc.toFixed(2)+' t':(c.change>0?'+':'')+c.change.toFixed(1)+'%';
    const chgCol=c.change>0?'var(--a1)':'var(--a3)',chgSign=c.change>0?'↑':'↓';
    const vs=c.co2series,mn=Math.min(...vs),mx=Math.max(...vs),rng=mx-mn||1;
    const W=180,H=28,p=2;
    const pts=vs.map((v,j)=>`${p+(j/(vs.length-1))*(W-p*2)},${H-p-(v-mn)/rng*(H-p*2)}`).join(' ');
    const card=document.createElement('div');
    card.className='glance-card';
    card.style.cssText=`border-top:3px solid ${col};`;
    card.innerHTML=`<span class="gc-rank">#${i+1}</span><div class="gc-country"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${col};flex-shrink:0"></span>${c.country}</div><div class="gc-region">${c.reg}</div><div class="gc-bar-wrap"><div class="gc-bar" style="width:${barPct}%;background:${col}"></div></div><div class="gc-vals"><div><div class="gc-main" style="color:${col}">${mainVal}</div><div class="gc-sub">${metric==='co2'?'Total CO₂ '+latestYr:metric==='pc'?'Per Capita '+latestYr:'Change 1990→2023'}</div></div><div style="text-align:right"><div class="gc-chg" style="color:${chgCol}">${chgSign}${Math.abs(c.change).toFixed(1)}%</div><div class="gc-sub">${c.share.toFixed(2)}% global</div></div></div><svg class="glance-sparkline" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><polyline points="${pts}" fill="none" stroke="${col}" stroke-width="1.8" stroke-linejoin="round" opacity="0.8"/><polygon points="${p},${H-p} ${pts} ${W-p},${H-p}" fill="${col}" opacity="0.1"/></svg>`;
    card.onclick=()=>{switchTab('trends');const s=document.getElementById('trendSel');if([...s.options].some(o=>o.value===c.country)){s.value=c.country;updateTrend();}};
    grid.appendChild(card);
  });
}

/* ════════════════════════════════════════
   CARBON FOOTPRINT TAB
════════════════════════════════════════ */
let fpTimer=null,fpFrameIdx=0;

function renderFootprint(){
  drawFootSVG();drawRankShift();
  const slider=document.getElementById('fpSlider');
  slider.min=0;slider.max=window.ALL_YEARS.length-1;slider.value=0;
  fpFrameIdx=0;
  document.getElementById('fpYearDisp').textContent=window.ALL_YEARS[0];
  document.getElementById('fpSliderYr').textContent=window.ALL_YEARS[0];
  drawFpTreemap(0);
  drawImproversWorseners();
}

function drawFootSVG(){
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const svg=document.getElementById('footSvg');
  const latestYr=window.ALL_YEARS.at(-1);
  const yrData=window.DATA.mapData.filter(d=>d.Year===latestYr);
  const regionTotals={};
  yrData.forEach(d=>{const r=window.DATA.regionMap[d.Country]||'Other';regionTotals[r]=(regionTotals[r]||0)+d.CO2_mt;});
  const grand=Object.values(regionTotals).reduce((a,b)=>a+b,0);
  const regionColors={'Asia':'#ff5f2e','Europe':'#9b7ff4','North America':'#f5c842','South America':'#2edfb4','Africa':'#f06bac','Oceania':'#38c4f5','Other':'#8a96b3'};
  const footFill=isDark?'#1a2035':'#dde3f5',footStroke=isDark?'rgba(255,255,255,0.15)':'rgba(0,0,0,0.2)';
  const textCol=isDark?'#e4e9f4':'#1a2040',subCol=isDark?'#8a96b3':'#5a6480';
  const toes=[{region:'Asia',cx:155,cy:62,r:42,label:'Asia'},{region:'North America',cx:92,cy:80,r:32,label:'N. America'},{region:'Europe',cx:210,cy:95,r:28,label:'Europe'},{region:'Africa',cx:60,cy:120,r:22,label:'Africa'},{region:'South America',cx:245,cy:118,r:20,label:'S. America'}];
  let html=`<ellipse cx="160" cy="340" rx="110" ry="145" fill="${footFill}" stroke="${footStroke}" stroke-width="1.5"/><ellipse cx="160" cy="465" rx="85" ry="45" fill="${footFill}" stroke="${footStroke}" stroke-width="1.5"/><path d="M 60 350 Q 90 300 120 340" stroke="${footStroke}" stroke-width="2" fill="none"/><text x="160" y="340" text-anchor="middle" font-family="Syne,sans-serif" font-size="15" font-weight="700" fill="${textCol}">Global CO₂</text><text x="160" y="362" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="12" fill="${subCol}">${(grand/1000).toFixed(1)} Gt (${latestYr})</text><line x1="110" y1="390" x2="210" y2="390" stroke="${footStroke}" stroke-width="1"/><line x1="100" y1="410" x2="220" y2="410" stroke="${footStroke}" stroke-width="1"/><line x1="95" y1="430" x2="225" y2="430" stroke="${footStroke}" stroke-width="1"/>`;
  toes.forEach(t=>{const pct=((regionTotals[t.region]||0)/grand*100),col=regionColors[t.region]||'#8a96b3',opacity=0.3+pct/100*0.7;html+=`<circle cx="${t.cx}" cy="${t.cy}" r="${t.r}" fill="${col}" opacity="${opacity.toFixed(2)}" stroke="${col}" stroke-width="1.5"/><text x="${t.cx}" y="${t.cy-4}" text-anchor="middle" font-family="Syne,sans-serif" font-size="9" font-weight="700" fill="white">${t.label}</text><text x="${t.cx}" y="${t.cy+8}" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="8.5" fill="white">${pct.toFixed(1)}%</text>`;});
  const legRegions=Object.entries(regionTotals).sort((a,b)=>b[1]-a[1]);
  html+=`<text x="160" y="290" text-anchor="middle" font-family="Syne,sans-serif" font-size="11" font-weight="700" fill="${subCol}" letter-spacing="1">REGION BREAKDOWN</text>`;
  let legX=30,legY=310;
  legRegions.forEach(([r,v],i)=>{
    const col=regionColors[r]||'#8a96b3';
    if(i===4){legX=30;legY+=18;}
    html+=`<rect x="${legX}" y="${legY}" width="8" height="8" rx="2" fill="${col}"/><text x="${legX+11}" y="${legY+7}" font-family="DM Sans,sans-serif" font-size="8.5" fill="${subCol}">${r} ${(v/1000).toFixed(1)}Gt</text>`;
    legX+=100;if(legX>280){legX=30;legY+=14;}
  });
  svg.innerHTML=html;
}

function drawRankShift(){
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const D=window.DATA;
  const yr2007=D.mapData.filter(d=>d.Year===2007).sort((a,b)=>b.CO2_mt-a.CO2_mt).slice(0,20);
  const yr2023=D.mapData.filter(d=>d.Year===2023).sort((a,b)=>b.CO2_mt-a.CO2_mt).slice(0,20);
  const rank2007={},rank2023={};
  yr2007.forEach((d,i)=>rank2007[d.Country]=i+1);
  yr2023.forEach((d,i)=>rank2023[d.Country]=i+1);
  const allCts=[...new Set([...yr2007.map(d=>d.Country),...yr2023.map(d=>d.Country)])];
  const rows=allCts.map(c=>({country:c,r2007:rank2007[c]||21,r2023:rank2023[c]||21,shift:(rank2007[c]||21)-(rank2023[c]||21),co2_2023:yr2023.find(d=>d.Country===c)?.CO2_mt||0})).sort((a,b)=>a.r2023-b.r2023);
  const textCol=isDark?'#e4e9f4':'#1a2040';
  const traces=[{type:'scatter',mode:'markers+text',name:'2007 Rank',x:rows.map(r=>r.r2007),y:rows.map(r=>r.country),marker:{size:12,color:rows.map(r=>getCC(r.country)),symbol:'circle',line:{color:'rgba(0,0,0,0.3)',width:1}},text:rows.map(r=>r.r2007<=20?'#'+r.r2007:'—'),textposition:'middle right',textfont:{size:9,color:isDark?'#8a96b3':'#5a6480'},hovertemplate:'<b>%{y}</b><br>2007 Rank: %{x}<extra></extra>'},{type:'scatter',mode:'markers+text',name:'2023 Rank',x:rows.map(r=>r.r2023),y:rows.map(r=>r.country),marker:{size:14,color:rows.map(r=>getCC(r.country)),symbol:'diamond',line:{color:'rgba(0,0,0,0.4)',width:1.5}},text:rows.map(r=>r.r2023<=20?'#'+r.r2023:'—'),textposition:'middle left',textfont:{size:9,color:isDark?'#8a96b3':'#5a6480'},hovertemplate:'<b>%{y}</b><br>2023 Rank: %{x}<extra></extra>'}];
  rows.forEach(r=>{const col=r.shift>0?'rgba(46,223,180,0.35)':r.shift<0?'rgba(255,95,46,0.35)':'rgba(138,150,179,0.2)';traces.push({type:'scatter',mode:'lines',x:[r.r2007,r.r2023],y:[r.country,r.country],line:{color:col,width:2},showlegend:false,hoverinfo:'skip'});});
  Plotly.newPlot('rankShiftChart',traces,{...getDarkLayout(),title:{text:'<b>Rank: ◆ 2023  ●  2007</b>',font:{size:13,color:textCol},x:.5},xaxis:{...getDarkLayout().xaxis,title:'Global Rank (lower = more CO₂)',autorange:'reversed',range:[22,0],dtick:5},yaxis:{...getDarkLayout().yaxis,automargin:true},hovermode:'closest',legend:{bgcolor:'rgba(0,0,0,0)',font:{color:textCol,size:11}},margin:{l:130,r:20,t:44,b:44}},PC);
}

/* ── FIXED: Footprint Treemap uses Plotly.react for smooth updates ── */
let fpTreemapInitialized=false;

function drawFpTreemap(yearIdx){
  const isDark=document.documentElement.getAttribute('data-theme')==='dark';
  const yr=window.ALL_YEARS[yearIdx];
  const yrData=window.DATA.mapData.filter(d=>d.Year===yr).sort((a,b)=>b.CO2_mt-a.CO2_mt).slice(0,20);
  const textCol=isDark?'#e4e9f4':'#1a2040';

  const trace=[{
    type:'treemap',
    labels:yrData.map(d=>d.Country),
    parents:yrData.map(()=>''),
    values:yrData.map(d=>d.CO2_mt),
    marker:{colors:yrData.map(d=>getCC(d.Country)),line:{width:3,color:isDark?'#080b12':'#f0f2f8'}},
    texttemplate:'<b>%{label}</b><br>%{value:.0f} Mt',
    hovertemplate:'<b>%{label}</b><br>CO₂: %{value:.1f} Mt<br>Click for trend →<extra></extra>',
    textfont:{family:"'Syne',sans-serif",size:13,color:'#fff'},
    tiling:{packing:'squarify'},
    pathbar:{visible:false}
  }];

  const layout={
    paper_bgcolor:'rgba(0,0,0,0)',
    plot_bgcolor:'rgba(0,0,0,0)',
    title:{text:`<b>Top 20 Emitters — ${yr}</b>`,font:{size:16,color:textCol},x:.5},
    margin:{l:4,r:4,t:48,b:4},
    font:{family:"'DM Sans',sans-serif",color:textCol}
  };

  if(!fpTreemapInitialized){
    Plotly.newPlot('fpTreemap',trace,layout,PC);
    fpTreemapInitialized=true;
    const el=document.getElementById('fpTreemap');
    el.on('plotly_click',function(data){
      const pt=data.points?.[0];if(!pt) return;
      const country=pt.label;
      switchTab('trends');
      const s=document.getElementById('trendSel');
      if([...s.options].some(o=>o.value===country)){s.value=country;updateTrend();}
    });
  } else {
    Plotly.react('fpTreemap',trace,layout,PC);
  }
}

function jumpFpFrame(idx){
  fpFrameIdx=idx;
  document.getElementById('fpYearDisp').textContent=window.ALL_YEARS[idx];
  document.getElementById('fpSliderYr').textContent=window.ALL_YEARS[idx];
  document.getElementById('fpSlider').value=idx;
  drawFpTreemap(idx);
}

function toggleFpAnim(){
  if(fpTimer){clearInterval(fpTimer);fpTimer=null;document.getElementById('fpPlayBtn').textContent='▶ Animate';return;}
  if(fpFrameIdx>=window.ALL_YEARS.length-1) fpFrameIdx=0;
  document.getElementById('fpPlayBtn').textContent='⏸ Pause';
  fpTimer=setInterval(function(){
    drawFpTreemap(fpFrameIdx);
    document.getElementById('fpSlider').value=fpFrameIdx;
    document.getElementById('fpSliderYr').textContent=window.ALL_YEARS[fpFrameIdx];
    document.getElementById('fpYearDisp').textContent=window.ALL_YEARS[fpFrameIdx];
    fpFrameIdx++;
    if(fpFrameIdx>=window.ALL_YEARS.length){
      clearInterval(fpTimer);fpTimer=null;
      document.getElementById('fpPlayBtn').textContent='▶ Animate';
    }
  },700);
}

function resetFpAnim(){
  if(fpTimer){clearInterval(fpTimer);fpTimer=null;}
  document.getElementById('fpPlayBtn').textContent='▶ Animate';
  fpFrameIdx=0;
  fpTreemapInitialized=false;
  jumpFpFrame(0);
}

function drawImproversWorseners(){
  const D=window.DATA;
  const yr2007=D.mapData.filter(d=>d.Year===2007),yr2023=D.mapData.filter(d=>d.Year===2023);
  const changes=[];
  yr2023.forEach(d23=>{
    const d07=yr2007.find(d=>d.Country===d23.Country);if(!d07) return;
    const pct=((d23.CO2_mt-d07.CO2_mt)/d07.CO2_mt*100);
    changes.push({country:d23.Country,pct,co2_2007:d07.CO2_mt,co2_2023:d23.CO2_mt});
  });
  const improvers=[...changes].sort((a,b)=>a.pct-b.pct).slice(0,10);
  const worseners=[...changes].sort((a,b)=>b.pct-a.pct).slice(0,10);
  const maxImp=Math.abs(improvers[0]?.pct||1),maxWor=worseners[0]?.pct||1;
  document.getElementById('improversList').innerHTML=improvers.map((d,i)=>`<div class="improve-row"><div class="ir-rank" style="color:var(--a3)">${i+1}</div><div style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${getCC(d.country)};flex-shrink:0"></div><div class="ir-name">${d.country}</div><div class="ir-bar-wrap"><div class="ir-bar" style="width:${(Math.abs(d.pct)/maxImp*100).toFixed(1)}%;background:var(--a3)"></div></div><div class="ir-pct" style="color:var(--a3)">${d.pct.toFixed(1)}%</div></div>`).join('');
  document.getElementById('worsenersList').innerHTML=worseners.map((d,i)=>`<div class="worsen-row"><div class="ir-rank" style="color:var(--a1)">${i+1}</div><div style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${getCC(d.country)};flex-shrink:0"></div><div class="ir-name">${d.country}</div><div class="ir-bar-wrap"><div class="ir-bar" style="width:${(d.pct/maxWor*100).toFixed(1)}%;background:var(--a1)"></div></div><div class="ir-pct" style="color:var(--a1)">+${d.pct.toFixed(1)}%</div></div>`).join('');
}

/* ════ BOOTSTRAP ════ */
window.addEventListener('DOMContentLoaded',init);
