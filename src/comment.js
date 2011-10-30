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

