(function(){var q=document.getElementById("q"),r=document.getElementById("res"),D=null;
function norm(s){return s.toLowerCase().normalize("NFC")}
function go(){var v=norm(q.value.trim());if(v.length<2){r.innerHTML="";return}
 function run(){var out=[];D.forEach(function(d){var t=norm(d.x),i=t.indexOf(v);if(i>=0||norm(d.t).indexOf(v)>=0){var s=d.x.substr(Math.max(0,i-50),140).replace(/</g,"&lt;");out.push('<a href="'+d.u+'"><b>'+d.g+" – "+d.t+"</b><br><small>…"+s+"…</small></a>")}});
  r.innerHTML=out.length?out.join(""):"<small>Không tìm thấy.</small>"}
 if(D)run();else fetch("assets/search.json").then(function(x){return x.json()}).then(function(j){D=j;run()})}
q.addEventListener("input",go)})();