"""
Utilities for use in Mako markup.
"""

import markupsafe


def format_html(fmt, **kwargs):
    """Format a text string, using HTML inserts.

    For use with a translated string, which is interpreted as text, not HTML,
    but which needs to have HTML elements inserted into it.  The result will
    be HTML, ready for direct inclusion into a template::

        ${format_html(_("Write & send {start}email{end}"),
            start="<a href='mailto:ned@edx.org'>",
            end="</a>",
            ) | n }

    Arguments:
        fmt (unicode): the format string: text, not HTML.
        kwargs (dict): the named data to be inserted into `fmt`.

    Returns:
        unicode, an HTML string.

    """

    markup_args = {k:markupsafe.Markup(v) for k,v in kwargs.iteritems()}
    return markupsafe.escape(fmt).format(**markup_args)
