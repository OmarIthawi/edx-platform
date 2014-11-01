# -*- coding: utf-8 -*-
"""
Tests for util.markup
"""

import unittest

import ddt

from edxmako.template import Template
from util.markup import format_html


@ddt.ddt
class FormatHtmlTest(unittest.TestCase):

    @ddt.data(
        (u"hello", u"hello"),
        (u"<hello>", u"&lt;hello&gt;"),
        (u"It's cool", u"It&#39;s cool"),
        (u'"cool," she said.', u'&#34;cool,&#34; she said.'),
        (u"Stop & Shop", u"Stop &amp; Shop"),
        (u"<a>нтмℓ-єѕ¢αρє∂</a>", u"&lt;a&gt;нтмℓ-єѕ¢αρє∂&lt;/a&gt;"),
    )
    def test_simple(self, (before, after)):
        self.assertEqual(unicode(format_html(before)), after)

    def test_formatting(self):
        # The whole point of this function is to make sure this works:
        out = format_html(u"Point & click {start}here{end}!",
            start="<a href='http://edx.org'>",
            end="</a>",
        )
        self.assertEqual(
            unicode(out),
            u"Point &amp; click <a href='http://edx.org'>here</a>!",
        )

    def test_mako(self):
        # The default_filters used here have to match the ones in edxmako.
        out = Template("""
            <%! from util.markup import format_html %>
            ${format_html(
                u"A & {BC}",
                BC="B & C"
            ) | n}
            """, default_filters=['decode.utf8', 'h']).render({})
        self.assertEqual(out.strip(), u"A &amp; B & C")
