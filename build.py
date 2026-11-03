#!/usr/bin/env python3
"""Build trang web tĩnh từ 2 file .docx trong source/ -> thư mục docs/ (dùng cho GitHub Pages).
Chạy:  python3 build.py            (cần pandoc đã cài)
Đổi mật khẩu: sửa "password" trong config.json rồi chạy lại.
"""
import json, re, os, shutil, subprocess, hashlib, html, sys, secrets
ROOT=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(ROOT,'source'); OUT=os.path.join(ROOT,'docs')
cfg=json.load(open(os.path.join(ROOT,'config.json'),encoding='utf-8'))
ov=json.load(open(os.path.join(SRC,'overview.json'),encoding='utf-8'))
GRADES={'7':{'docx':'KHBD_Tin7_DA_SUA.docx','label':'Tin học 7','ids':['b2','b3','b5','b6','b7a','b7b','b14','b15','b16a','b16b']},
        '8':{'docx':'KHBD_Tin8_DA_SUA.docx','label':'Tin học 8','ids':['b2','b4','b5','b8a','b8b','b12','b13','b15','b16a','b16b']}}
MARK='<p><strong>KẾ HOẠCH BÀI DẠY</strong></p>'

def run_pandoc(g):
    tmp=os.path.join(ROOT,'.tmp'+g); shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    subprocess.run(['pandoc',os.path.join(SRC,GRADES[g]['docx']),'-t','html5','--wrap=none','--extract-media=media'+g,'-o','t.html'],cwd=tmp,check=True)
    return tmp,open(os.path.join(tmp,'t.html'),encoding='utf-8').read()
def strip(s): return html.unescape(re.sub(r'<[^>]+>','',s)).strip()

pages=[]  # metadata for all lessons
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT+'/assets'); os.makedirs(OUT+'/tai-ve')
for g,info in GRADES.items():
    tmp,h=run_pandoc(g)
    chunks=[MARK+c for c in h.split(MARK) if c.strip()]
    assert len(chunks)==len(info['ids']),(g,len(chunks))
    os.makedirs(f'{OUT}/tin{g}')
    if cfg.get('include_images',True) and os.path.isdir(f'{tmp}/media{g}/media'): shutil.copytree(f'{tmp}/media{g}/media',f'{OUT}/tin{g}/media')
    for idx,(bid,c) in enumerate(zip(info['ids'],chunks)):
        paras=re.findall(r'<p>(.*?)</p>',c)[:8]
        txt=[strip(p) for p in paras]
        chude=next((t for t in txt if t.upper().startswith('CHỦ ĐỀ')),'')
        bai=next((t for t in txt if t.upper().startswith('BÀI')),bid)
        tg=next((t for t in txt if t.startswith('Thời gian')),'')
        c=re.sub(r'media'+g+r'/media/',('media/' if cfg.get('include_images',True) else 'x/'),c)
        c=re.sub(r'(<img[^>]*?)style="[^"]*"',r'\1',c)
        if not cfg.get('include_images',True): c=re.sub(r'<img[^>]*>','<em>[Hình minh hoạ: xem SGK]</em>',c)
        c=re.sub(r'(<table.*?</table>)',r'<div class="tw">\1</div>',c,flags=re.S)
        pages.append(dict(grade=g,id=bid,slug=f'tin{g}/{bid}.html',idx=idx,chude=chude,bai=bai,tg=tg,html=c,text=strip(re.sub(r'<(?:/p|/tr|/li|br)[^>]*>',' ',c))))
    shutil.rmtree(tmp,ignore_errors=True)

# ---------- password gate ----------
salt=secrets.token_hex(8); pw=cfg['password']
pwhash=hashlib.sha256((salt+pw).encode()).hexdigest()
open(OUT+'/assets/gate.js','w',encoding='utf-8').write('''(function(){
var SALT="%s",HASH="%s",K="khbd_ok_v1";
function sha(s){return crypto.subtle.digest("SHA-256",new TextEncoder().encode(s)).then(function(b){return Array.from(new Uint8Array(b)).map(function(x){return x.toString(16).padStart(2,"0")}).join("")})}
function unlock(){document.documentElement.classList.remove("locked");var g=document.getElementById("gate");if(g)g.remove();}
if(sessionStorage.getItem(K)===HASH){unlock();return}
document.addEventListener("DOMContentLoaded",function(){
 var d=document.createElement("div");d.id="gate";
 d.innerHTML='<form><h2>Trang có mật khẩu</h2><p>Nhập mật khẩu để xem kế hoạch bài dạy.</p><input type="password" id="pw" placeholder="Mật khẩu" autofocus><button type="submit">Vào xem</button><div id="err"></div></form>';
 document.body.appendChild(d);
 d.querySelector("form").addEventListener("submit",function(e){e.preventDefault();
  if(!window.crypto||!crypto.subtle){document.getElementById("err").textContent="Trình duyệt cần mở trang qua https.";return}
  sha(SALT+document.getElementById("pw").value).then(function(h){if(h===HASH){sessionStorage.setItem(K,HASH);unlock()}else{document.getElementById("err").textContent="Sai mật khẩu, thử lại."}})});
});})();
'''%(salt,pwhash))

# ---------- css ----------
open(OUT+'/assets/style.css','w',encoding='utf-8').write(r'''
:root{--navy:#1F3864;--blue:#2E75B6;--light:#EAF1FB;--line:#C9D5E6;--text:#1c2430;--muted:#5b6678}
*{box-sizing:border-box}html{scroll-behavior:smooth}
html.locked body>*:not(#gate){display:none!important}
body{margin:0;font-family:-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;color:var(--text);line-height:1.6;background:#f6f8fc}
#gate{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1F3864,#2E75B6);z-index:99}
#gate form{background:#fff;padding:32px;border-radius:14px;width:min(92vw,360px);box-shadow:0 20px 60px rgba(0,0,0,.3)}
#gate h2{margin:0 0 6px;color:var(--navy)}#gate p{margin:0 0 16px;color:var(--muted)}
#gate input{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:8px;font-size:16px;margin-bottom:12px}
#gate button{width:100%;padding:11px;border:0;border-radius:8px;background:var(--blue);color:#fff;font-size:16px;cursor:pointer}
#err{color:#b3261e;margin-top:10px;font-size:14px}
header.top{background:var(--navy);color:#fff;padding:12px 20px;display:flex;gap:16px;align-items:center;flex-wrap:wrap;position:sticky;top:0;z-index:10}
header.top a{color:#fff;text-decoration:none}header.top .brand{font-weight:700;font-size:17px}
header.top nav{display:flex;gap:14px;font-size:14px;margin-left:auto}header.top nav a{opacity:.9}header.top nav a:hover{opacity:1;text-decoration:underline}
.layout{display:grid;grid-template-columns:270px 1fr;max-width:1280px;margin:0 auto}
aside.side{padding:18px 14px;border-right:1px solid var(--line);background:#fff;height:calc(100vh - 52px);position:sticky;top:52px;overflow:auto;font-size:14px}
aside.side h4{margin:14px 0 6px;color:var(--navy);font-size:13px;text-transform:uppercase;letter-spacing:.04em}
aside.side a{display:block;padding:5px 8px;border-radius:6px;color:var(--text);text-decoration:none}
aside.side a:hover{background:var(--light)}aside.side a.on{background:var(--blue);color:#fff}
main{padding:24px 28px;min-width:0}
.hero{background:#fff;border:1px solid var(--line);border-radius:14px;padding:26px;margin-bottom:22px}
.hero h1{margin:0 0 6px;color:var(--navy);font-size:28px}.hero p{margin:0;color:var(--muted)}
.hero .actions{margin-top:16px;display:flex;gap:10px;flex-wrap:wrap}
.btn{display:inline-block;padding:9px 15px;border-radius:8px;background:var(--blue);color:#fff;text-decoration:none;font-size:14px}
.btn.alt{background:#fff;color:var(--blue);border:1px solid var(--blue)}
#q{width:100%;padding:11px 14px;border:1px solid var(--line);border-radius:10px;font-size:16px;margin-bottom:8px}
#res{margin-bottom:18px}#res a{display:block;background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin-bottom:8px;text-decoration:none;color:var(--text)}
#res small{color:var(--muted)}mark{background:#ffe58a}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;margin-bottom:26px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--text);display:block}
.card:hover{border-color:var(--blue);box-shadow:0 4px 14px rgba(46,117,182,.15)}
.card b{color:var(--navy);display:block}.card span{color:var(--muted);font-size:13px}
h2.sec{color:var(--navy);margin:8px 0 12px}
article.lesson{background:#fff;border:1px solid var(--line);border-radius:14px;padding:26px 30px;overflow-wrap:anywhere}
article.lesson>p:first-child{margin-top:0}
article.lesson p{margin:.5em 0}article.lesson ul{padding-left:22px}
.tw{overflow-x:auto;margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid var(--line);padding:6px 9px;vertical-align:top;text-align:left}
tr:first-child td,th{background:var(--light)}
img{max-width:100%;height:auto;border-radius:6px}
.pager{display:flex;justify-content:space-between;gap:10px;margin-top:20px}
.crumb{color:var(--muted);font-size:14px;margin-bottom:10px}
.ovt{margin:10px 0 24px}.ovt td{font-size:13.5px}
.note{background:#fff8e1;border:1px solid #f0d98a;border-radius:10px;padding:12px 16px;margin:14px 0;font-size:14px}
footer{text-align:center;color:var(--muted);font-size:13px;padding:24px}
@media(max-width:860px){.layout{grid-template-columns:1fr}aside.side{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}main{padding:16px}article.lesson{padding:16px}}
@media print{header.top,aside.side,.pager,footer,.actions{display:none!important}.layout{display:block}body{background:#fff}article.lesson{border:0;padding:0}}
''')

# ---------- shared layout ----------
def side(cur,depth):
    p='../'*depth
    s=f'<h4>Trang chính</h4><a href="{p}index.html"{" class=on" if cur=="index" else ""}>Trang chủ</a><a href="{p}tong-quan.html"{" class=on" if cur=="tq" else ""}>Tổng quan chỉnh sửa</a>'
    for g,info in GRADES.items():
        s+=f'<h4>{info["label"]}</h4>'
        for pg in [x for x in pages if x['grade']==g]:
            s+=f'<a href="{p}{pg["slug"]}"{" class=on" if cur==pg["slug"] else ""}>{html.escape(pg["bai"].title().replace("Bài","Bài") if False else pg["bai"])}</a>'
    return s
def shell(title,body,cur,depth):
    p='../'*depth
    return f'''<!doctype html><html lang="vi" class="locked"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>{html.escape(title)} – {html.escape(cfg["site_title"])}</title><link rel="stylesheet" href="{p}assets/style.css"><script src="{p}assets/gate.js"></script></head><body>
<header class="top"><a class="brand" href="{p}index.html">{html.escape(cfg["site_title"])}</a><nav><a href="{p}index.html">Trang chủ</a><a href="{p}tong-quan.html">Tổng quan chỉnh sửa</a><a href="{p}index.html#tai-ve">Tải file</a></nav></header>
<div class="layout"><aside class="side">{side(cur,depth)}</aside><main>{body}</main></div><footer>{html.escape(cfg["site_subtitle"])}</footer></body></html>'''

# ---------- lesson pages ----------
for i,pg in enumerate(pages):
    same=[x for x in pages if x['grade']==pg['grade']]; k=same.index(pg)
    prv=same[k-1] if k>0 else None; nxt=same[k+1] if k<len(same)-1 else None
    pager='<div class="pager">'+(f'<a class="btn alt" href="{prv["id"]}.html">← {html.escape(prv["bai"][:38])}</a>' if prv else '<span></span>')+(f'<a class="btn alt" href="{nxt["id"]}.html">{html.escape(nxt["bai"][:38])} →</a>' if nxt else '<span></span>')+'</div>'
    body=f'<div class="crumb"><a href="../index.html">Trang chủ</a> / {GRADES[pg["grade"]]["label"]} / {html.escape(pg["bai"])}</div><article class="lesson">{pg["html"]}</article>{pager}'
    open(f'{OUT}/{pg["slug"]}','w',encoding='utf-8').write(shell(pg['bai'],body,pg['slug'],1))

# ---------- search index ----------
json.dump([dict(t=p['bai'],g=GRADES[p['grade']]['label'],u=p['slug'],x=p['text'][:20000]) for p in pages],open(OUT+'/assets/search.json','w',encoding='utf-8'),ensure_ascii=False)
open(OUT+'/assets/search.js','w',encoding='utf-8').write('''(function(){var q=document.getElementById("q"),r=document.getElementById("res"),D=null;
function norm(s){return s.toLowerCase().normalize("NFC")}
function go(){var v=norm(q.value.trim());if(v.length<2){r.innerHTML="";return}
 function run(){var out=[];D.forEach(function(d){var t=norm(d.x),i=t.indexOf(v);if(i>=0||norm(d.t).indexOf(v)>=0){var s=d.x.substr(Math.max(0,i-50),140).replace(/</g,"&lt;");out.push('<a href="'+d.u+'"><b>'+d.g+" – "+d.t+"</b><br><small>…"+s+"…</small></a>")}});
  r.innerHTML=out.length?out.join(""):"<small>Không tìm thấy.</small>"}
 if(D)run();else fetch("assets/search.json").then(function(x){return x.json()}).then(function(j){D=j;run()})}
q.addEventListener("input",go)})();''')

# ---------- index ----------
cards=''
for g,info in GRADES.items():
    cards+=f'<h2 class="sec">{info["label"]}</h2><div class="grid">'
    for pg in [x for x in pages if x['grade']==g]:
        cards+=f'<a class="card" href="{pg["slug"]}"><b>{html.escape(pg["bai"])}</b><span>{html.escape(pg["chude"].title() if False else pg["chude"])}</span><br><span>{html.escape(pg["tg"])}</span></a>'
    cards+='</div>'
dl=f'''<h2 class="sec" id="tai-ve">Tải file</h2><div class="grid">
<a class="card" href="tai-ve/KHBD_Tin7_DA_SUA.docx"><b>Tin học 7 (.docx)</b><span>Bản hoàn chỉnh đã sửa</span></a>
<a class="card" href="tai-ve/KHBD_Tin8_DA_SUA.docx"><b>Tin học 8 (.docx)</b><span>Bản hoàn chỉnh đã sửa</span></a>
<a class="card" href="tai-ve/TONG_QUAN_CHINH_SUA_KHBD.pdf"><b>Tổng quan chỉnh sửa (.pdf)</b><span>Tóm tắt các thay đổi</span></a></div>'''
index=f'''<section class="hero"><h1>{html.escape(cfg["site_title"])}</h1><p>{html.escape(cfg["site_subtitle"])}</p>
<div class="actions"><a class="btn" href="tin7/b2.html">Bắt đầu với Tin 7</a><a class="btn" href="tin8/b2.html">Bắt đầu với Tin 8</a><a class="btn alt" href="tong-quan.html">Xem tổng quan chỉnh sửa</a></div></section>
<input id="q" type="search" placeholder="Tìm trong tất cả giáo án (ví dụ: nổi bọt, bảng tính, bản quyền)"><div id="res"></div>
{cards}{dl}<script src="assets/search.js"></script>'''
open(OUT+'/index.html','w',encoding='utf-8').write(shell('Trang chủ',index,'index',0))

# ---------- overview page ----------
def tb(rows,cls='ovt'):
    h='<div class="tw"><table class="%s"><tr>'%cls+''.join(f'<th>{c}</th>' for c in rows[0])+'</tr>'
    for r in rows[1:]: h+='<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>'
    return h+'</table></div>'
tq=f'''<section class="hero"><h1>Tổng quan các chỉnh sửa</h1><p>Đối chiếu với bảng giới hạn, Khung NLS (CV 3456), Khung năng lực AI (3439) và mẫu giáo án CV 5512.</p>
<div class="actions"><a class="btn" href="tai-ve/TONG_QUAN_CHINH_SUA_KHBD.pdf">Tải bản PDF</a></div></section>
<h2 class="sec">1. Kết luận từ review</h2><p>Phạm vi bài khớp bảng giới hạn (10 bài mỗi khối). Nội dung cốt lõi bám SGK, nhưng cả 20 bài đều có lỗi ở bốn nhóm: <b>vượt trang giới hạn</b>, <b>lệch mẫu 5512</b>, <b>mã NLS và mã AI không đúng khung</b>, và <b>lỗi kiến thức, chính tả, tiêu đề, dòng ghi chú soạn thảo còn sót</b>.</p>
<h2 class="sec">2. Các nhóm sửa chung</h2>{tb(ov['rows'])}
<h2 class="sec">3. Chi tiết theo từng bài – Tin học 7</h2>{tb(ov['r7'])}
<h2 class="sec">Tin học 8</h2>{tb(ov['r8'])}
<h2 class="sec">4. Việc giáo viên nên làm trước khi dùng</h2><ul>{''.join(f'<li>{t}</li>' for t in ov['todo'])}</ul>'''
open(OUT+'/tong-quan.html','w',encoding='utf-8').write(shell('Tổng quan chỉnh sửa',tq,'tq',0))

# ---------- downloads, misc ----------
for f in ['KHBD_Tin7_DA_SUA.docx','KHBD_Tin8_DA_SUA.docx','TONG_QUAN_CHINH_SUA_KHBD.pdf']: shutil.copy(os.path.join(SRC,f),OUT+'/tai-ve/'+f)
open(OUT+'/.nojekyll','w').write('')
open(OUT+'/robots.txt','w').write('User-agent: *\nDisallow: /\n')
print('OK',len(pages),'bài ->',OUT)
