#!/usr/bin/python
"""
    The markdown preview cgi script of the psblog blog engine.

    A very simple script that takes markdown source code and returns HTML.

    Copyright (c) 2011 by Richard Wossal <richard@r-wos.org>

    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee is hereby granted, provided
    that the above copyright notice appear in all copies and that both that
    copyright notice and this permission notice appear in supporting
    documentation. This software is provided "as is" without express or
    implied warranty.
"""
import cgi   

import markdown

print("Content-Type: text/html\n\n")
fields = cgi.FieldStorage()
if "text" in fields and len(fields["text"].value) > 1:
    print(markdown.markdown(cgi.escape(fields["text"].value)))

