var state = 0;
var expire = new Date();
expire.setTime(expire.getTime()+1000*60*60*24*365)
var cookie_foot = "; expires="+expire.toUTCString()+"; path=/";
function switch_style() {
    tag = document.getElementsByTagName("link")[0];
    if (state == 0) {
        tag.href = tag.href.replace('style.css', 'alt_style.css');
        state = 1;
        document.cookie = "state=1"+cookie_foot;
    } else if (state == 1) {
        tag.href = tag.href.replace('alt_style.css', 'style.css');
        state = 0;
        document.cookie = "state=0"+cookie_foot;
    }
}
var cookies = document.cookie.split(';');
for (var i = 0; i < cookies.length; i++) {
    if (cookies[i].trim() == "state=1")
        switch_style();
}
var last_time = 0;
var staged = 0;
function preview_comment() {
    now = +new Date();
    if (last_time != 0 && now - last_time < 1000 * 2) {
        if (staged == 0) {
            staged = setTimeout("preview_comment()", 2000);
        }
        return;
    }
    clearTimeout(staged);
    staged = 0;
    text = document.getElementById("comment_text").value;
    xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            document.getElementById("comment_preview").innerHTML = xhr.responseText;
        }
    }
    xhr.open("GET",
        // XXX: use templating system for the url
        "http://blog.r-wos.org/markdown_preview.py"+"?text="+text,
        true);
    xhr.send(null); 
    last_time = now;
}

