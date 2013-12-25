from unittest import TestCase
import crawler

class TestParser(TestCase):
    baseurl = 'http://foo.net/'
    template = '<html><body> {0} </body></html>'

    def test_relative_absolute(self):
        testcase = """
        <a href="http://www.python.org/">foo</a>
        <a href="index.html">bar</a>
        <a class="reference external" href="/baz/"></a>
        """
        expected = set([
            'http://www.python.org/',
            self.baseurl + 'index.html',
            self.baseurl + 'baz/',
        ])

        actual = crawler.get_links(self.baseurl, self.template.format(testcase))
        self.assertEqual(expected, actual)

    def test_ignore_anchor(self):
        testcase = """
        <a href="index.html">bar</a>
        <a href="index.html#placeholder">bar</a>
        """
        expected = set([
            self.baseurl + 'index.html',
        ])

        actual = crawler.get_links(self.baseurl, self.template.format(testcase))
        self.assertEqual(expected, actual)
