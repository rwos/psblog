"""
    The main module of the psblog blog engine.

    Provides high-level functionality like adding new posts and comments
    and some low level helper stuff like logging and file I/O.

    Copyright (c) 2011 by Richard Wossal <richard@r-wos.org>

    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee is hereby granted, provided
    that the above copyright notice appear in all copies and that both that
    copyright notice and this permission notice appear in supporting
    documentation. This software is provided "as is" without express or
    implied warranty.
"""
import cgi   
import datetime as dt
import glob
import gzip
import os
import re
import time

import config
import html
import markdown

def compile_everything():
    """ Compile all the pages. """
    start = time.clock()
    posts = get_all_posts()
    for p in posts:
        create_single(p)
    create_multi(posts)
    create_rss(posts)
    create_stats(posts, start)
    create_errors()
    create_css()

def create_single(p):
    """ Create a single html file for a single post. """
    log_compile("creating single post")
    post_str = html.block(
        "".join([
            html.date(p["meta"]["datetime"]),
            html.h(2, p["meta"]["heading"]),
            html.p(p["html"]),
            html.author()]),
        "single")
    comments_str = ""
    for c in p["comments"]:
        comments_str += html.block(
            "".join([
                html.p(markdown.markdown(c["text"])),
                html.comment_meta(c)]))
    comment_form_str = html.comment_form(
        post_id(p["meta"]), post_url(p["meta"]))
    # write to file
    file_contents = post_str+comments_str+comment_form_str
    urlpath = str(p["meta"]["datetime"].year)+"/"+p["meta"]["url_heading"]
    write_out(urlpath+".html",
                  html.render_front(file_contents, p["meta"]["heading"]))
    log_compile("done")

def create_multi(posts):
    """ Create the overview index.html file. """
    log_compile("creating index page")
    o = ""
    for p in posts:
        o += html.block(
            "".join([
                html.h(2, html.post_link(p)),
                html.hex_dump(p["text"]),
                html.pre(
                    "-rw-r--r-- 1 rwos rwos "
                    +str(len(p["text"]))+" "
                    +html.date(p["meta"]["datetime"])+" "
                    +p["meta"]["url_heading"][0:20]),
                html.pre(str(len(p["comments"]))+" comment(s)")]))
    # TODO: pagination, with configurable limit
    write_out("index.html", html.render_front(o))
    log_compile("done")

def create_rss(posts):
    """ Create the RSS feed file. """
    log_compile("creating rss feed")
    o = ["<?xml version='1.0' encoding='utf-8'?>",
         "<rss version='2.0' xmlns:atom='http://www.w3.org/2005/Atom'>",
         "<channel>",
         "<atom:link href='", config.blog_url, "rss'",
         " rel='self' type='application/rss+xml'/>",
         "<title>", config.title, "</title>",
         "<description>", config.subtitle, "</description>",
         "<link>", config.blog_url, "</link>"]
    c = 0
    for p in posts:
        o += ["<item><title>", p["meta"]["heading"], "</title>",
              "<link>", post_url(p["meta"]), "</link>",
              "<guid>", post_url(p["meta"]), "</guid>",
              "<description><![CDATA[", p["html"], "]]></description>",
              "</item>"]
        c += 1
        if c == 10:
            break
    o.append("</channel></rss>")
    write_out("rss.xml", "".join(o))
    log_compile("done")

def create_stats(p, start):
    """ Create a small compilation statistic page. """
    write_out("stats.html", html.render_front(
        html.block("".join([
            html.h(2, "Statistics"),
            html.pre("".join([
                "last compile on ",
                dt.datetime.now().strftime("%A, %x %T"),
                "\n\nnumber of pages: ",
                str(len(p)),
                "\nrendering took ",
                str(time.clock()-start),
                " seconds"]))])), "statistics"))

def create_errors():
    """ Create custom error pages. """
    log_compile("creating error pages")
    content = {
        401: ("401 Unauthorized", "Go away."),
        403: ("403 Forbidden", "Yep, forbidden."),
        404: ("404 Not Found", "Sorry."),
        500: ("500 Internal Server Error", "Please try again later.")}
    for n, msg in content.items():
        write_out(str(n)+".html",
                  html.render_front(
                      html.block(html.h(2, msg[0])+html.p(msg[1])),
                      msg[0]))
    log_compile("done")

def create_css():
    """ Minify the css and write it to the output dir. """
    log_compile("creating error pages")
    css = readfile("style.css")
    write_out("style.css", html.minify_css(css))
    # alternative css
    css = readfile("alt_style.css")
    write_out("alt_style.css", html.minify_css(css))
    log_compile("done")

def get_post(post_id):
    """
        Return everything belonging to a single post as a dict.
        The keys are:
            "text" -- the source text, markdown format
            "html" -- the html generated from the text
            "meta" -- a dictionary containing meta information for the post
            "comments" -- a list of dicts, containing the comments
    """
    p = {}
    p["text"] = get_text(post_id)
    p["html"] = markdown.markdown(p["text"])
    p["meta"] = get_meta(post_id)
    p["comments"] = get_comments(post_id)
    return p

def get_all_posts():
    """ Return a list of all posts (see get_post for details). """
    log("getting all posts")
    posts = []
    for filename in glob.glob(config.data_dir+"*.txt"):
        post_id = filename.rstrip('.txt')
        p = get_post(post_id)
        posts.append(p)
    posts = sorted(posts, key=lambda x: x["meta"]["datetime"], reverse=True)
    log("done")
    return posts

def get_text(post_id):
    """ Return the text (i.e. markdown) for the given post id. """
    if not existing_post_id(post_id):
        return ""
    return readfile(post_id+".txt")

def get_comments(post_id):
    """ Return the comments for the given post id as a list. """
    if not existing_post_id(post_id):
        return []
    src = readfile(post_id+".comments")
    if len(src) < 2: # minimum "[]"
        return []
    try:
        # TODO: rm eval, use pickle(?)
        comments = eval(src)
    except SyntaxError:
        log_err("comments file for "+post_id+" is corrupted")
        return []
    # TODO: check if list and presence of keys
    return comments

def get_meta(post_id):
    """
        Return a dict containg some meta info for the post.
        The keys are:
            "heading" -- string, the heading
            "url_heading" -- string, escaped version of the heading
            "category" -- a string containg the category
            "datetime" -- a python datetime object with the post date
    """
    empty = {"heading":"","url_heading":"","category":"",
            "datetime":dt.datetime.now()}
    if not existing_post_id(post_id):
        return empty # whoops, that's not good
    src = readfile(post_id+".meta")
    if len(src) < 1:
        return empty # that's even worse...
    try:
        # TODO: rm eval, use pickle(?)
        meta = eval(src)
    except SyntaxError:
        log_err("meta file for "+post_id+" is corrupted")
        return empty # uh-uh
    # TODO: check presence of keys
    return meta

def save_text(text, post_id):
    """ Save the post's source text to disk. """
    if not valid_post_id(post_id):
        return
    write_data(post_id+".txt", text)

def save_meta(meta, post_id):
    """ Save the meta information for the given post id to disk. """
    if not valid_post_id(post_id):
        return
    write_data(post_id+".meta",
        # XXX HACK HACK HACK
        str(meta).replace("datetime.datetime", "dt.datetime"))

def save_comments(comments, post_id):
    """ Save the comments for the given post id to disk. """
    if not valid_post_id(post_id):
        return
    write_data(post_id+".comments", str(comments))

def existing_post_id(post_id):
    """ Return True if there is a post with the given post_id. """
    if not valid_post_id(post_id) or len(readfile(post_id+".txt")) < 1:
        log_err("existing_post_id: post "+post_id+" not found")
        return False
    return True

def valid_post_id(post_id):
    """ Return True if the post_id is valid (not necessarily existing). """
    if post_id.startswith(config.data_dir) and \
       post_id.count("..") == config.data_dir.count(".."):
        return True
    log_err("valid_post_id: post id "+post_id+" invalid")
    return False

def post_id(meta):
    """ Return the post id for a given meta info dictionary. """
    out = config.data_dir + \
        meta["url_heading"]+"_"+urlify(str(meta["datetime"]))
    if valid_post_id(out):
        return out
    return ""

def post_url(meta):
    """ Return the absolute post url for a given meta info dictionary. """
    return config.blog_url + \
        cgi.escape(str(meta["datetime"].year)+"/"+meta["url_heading"], True)

def urlify(s):
    """ Return a string that is usable in an URL and a filename. """
    # TODO: Does this regexp include non-ascii chars in some locales?
    s = re.sub("[^a-zA-Z0-9]", "-", s)
    s = s.strip("-")
    s = s.lower()
    return s

def log_err(msg):
    """ Log an error. """
    log("ERROR: "+msg)

def log(msg):
    """ Log a message. """
    log_file = config.log_dir+"psblog.log"
    try:
        size = os.path.getsize(log_file)
    except OSError:
        writefile(log_file, "")
        size = 0
    entry = dt.datetime.now().strftime(config.log_date_format)+" "+msg+"\n"
    if size < config.max_log_size * 1024:
        appendfile(log_file, entry)
    else:
        # TODO mail old log to author_email
        writefile(log_file, entry)

compile_log_started = 0
def log_compile(msg):
    """ Log a compilation step. """
    global compile_log_started
    if compile_log_started == 0:
        compile_log_started = time.clock()
        time_str = dt.datetime.now().strftime(config.log_date_format)
        writefile(config.log_dir+"compile.log",
                  "compiling started at "+time_str+"\n")
    appendfile(config.log_dir+"compile.log",
        "[%7.4f"%(time.clock()-compile_log_started)+"] "+msg+"\n")

def write_out(filename, html):
    """ Write a file, including a gzipped version, to the out_dir """
    writefile(config.out_dir+filename, html)
    f = gzip.open(config.out_dir+filename+".gz", 'wb')
    try:
        # XXX HACK
        # The whole unicode issue is a complete fuckup as of now.
        f.write(html.encode("utf8"))
    except UnicodeDecodeError:
        f.write(html)
    f.close()

def write_data(filename, data):
    """ Write a data file to the data_dir """
    writefile(config.data_dir+filename, data)

def readfile(filename):
    """ Read a file, don't care about errors. """
    try:
        f = open(filename, "r")
    except IOError:
        log_err("readfile: file "+filename+" not found")
        return ""
    s = f.read()
    f.close()
    return s

def writefile(filename, buf):
    """ Write a file, don't care about errors. """
    try:
        # XXX open wb??
        f = open(filename, "w")
    except IOError:
        log_err("writefile: file "+filename+" not written")
        return
    try: # XXX HACK
        f.write(buf.encode("utf8"))
    except UnicodeDecodeError:
        f.write(buf)
    f.close()

def appendfile(filename, buf):
    """ Append to a file, don't care about errors. """
    try:
        f = open(filename, "a")
    except IOError:
        log_err("appendfile: file "+filename+" not written")
        return
    try: # XXX HACK
        f.write(buf.encode("utf8"))
    except UnicodeDecodeError:
        f.write(buf)
    f.close()

