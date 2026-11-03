(function(){
var SALT="35795edf2fd6bd9b",HASH="c097783e36e13fee8ecc5f777a4a0e417899aeb898c923545fd92746683ee17e",K="khbd_ok_v1";
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
