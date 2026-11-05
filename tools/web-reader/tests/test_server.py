"""Tests for the web-reader MCP server: full text out, private addresses refused."""
import gzip
import ipaddress
import http.server
import threading
import zlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[1] / 'server.py'
_spec = spec_from_file_location('web_reader_server', _SCRIPT_PATH)
server = module_from_spec(_spec)
_spec.loader.exec_module(server)

def serving(content_type, body):
    """A fetcher that answers every URL with this content type and body."""
    def fetcher(url):
        return url, content_type, body
    return fetcher


def every_address_is_public(_address):
    """Stands in for is_public when a test serves from localhost."""
    return True


PAGE = b'''<html><head><title>Rules and skills</title><script>var counter = 1;</script></head>
<body><nav>Home | Blog | Pricing</nav>
<!-- tag manager snippet -->
<main><h1>Rules and skills</h1><p>Most rules had <b>no effect</b>.</p>
<ul><li>Three helped</li><li>Four hurt</li></ul>
<table><tr><th>Arm</th><th>Pass</th></tr><tr><td>No rules</td><td>50.0%</td></tr></table>
<p>The score is <math alttext="\\frac{a}{b}"><mi>a</mi></math> overall.</p></main>
<footer>Copyright</footer></body></html>'''


def test_html_keeps_structure_and_drops_scripts_comments_and_navigation():
    """A page reads as its body text, with headings, list items, table rows and math kept."""
    text = server.html_to_text(PAGE)
    assert text.startswith('# Rules and skills')
    assert 'Most rules had no effect.' in text
    assert '- Three helped' in text and '- Four hurt' in text
    assert 'Arm | Pass' in text and 'No rules | 50.0%' in text
    assert '\\frac{a}{b}' in text
    for leftover in ('counter', 'tag manager snippet', 'Pricing'):
        assert leftover not in text


def test_chunks_cover_the_document_exactly_and_end_with_an_end_marker():
    """Paging with the offsets each chunk names returns every character once, then says it ended."""
    lines = ''.join(f'Line {number} of the paper body.\n' for number in range(6000))
    reader = server.Reader(fetcher=serving('text/plain', lines.encode()))
    offset, bodies = 0, []
    while True:
        header, body = reader.read('https://example.org/paper', offset).split('----\n', 1)
        bodies.append(body)
        if 'End of document' in header:
            break
        offset = int(header.split('offset=')[1].split('.')[0])
    assert ''.join(bodies) == lines
    assert len(bodies) > 1
    assert all(len(body.encode()) <= server.CHUNK_BYTES for body in bodies)


def test_a_chunk_ends_at_a_line_break():
    """A chunk that is not the last stops after a newline, so no line is split between calls."""
    lines = ''.join(f'Sentence number {number} ends here.\n' for number in range(5000))
    reader = server.Reader(fetcher=serving('text/plain', lines.encode()))
    body = reader.read('https://example.org/a', 0).split('----\n', 1)[1]
    assert body.endswith('\n')


def test_an_offset_past_the_end_is_an_error():
    """Asking past the last character fails instead of returning an empty chunk."""
    reader = server.Reader(fetcher=serving('text/plain', b'short text'))
    with pytest.raises(server.ReadError):
        reader.read('https://example.org/a', 50)


class _QuietHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass


class _CountingHandler(_QuietHandler):
    requests = 0

    def do_GET(self):  # pylint: disable=invalid-name
        _CountingHandler.requests += 1
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'internal data')


@pytest.fixture(name='serve')
def fixture_serve():
    """Starts a local HTTP server for a handler class and returns its port."""
    servers = []

    def serve(handler):
        httpd = http.server.HTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        servers.append(httpd)
        return httpd.server_address[1]

    yield serve
    for httpd in servers:
        httpd.shutdown()
        httpd.server_close()


@pytest.fixture(name='local_server_port')
def fixture_local_server_port(serve):
    _CountingHandler.requests = 0
    return serve(_CountingHandler)


@pytest.mark.parametrize('host', ['127.0.0.1', 'localhost'])
def test_a_local_address_is_refused_before_any_request_is_sent(local_server_port, host):
    """A URL that reaches this machine, by address or by name, fails and the server sees nothing."""
    with pytest.raises(server.ReadError, match='not a public internet address'):
        server.fetch(f'http://{host}:{local_server_port}/')
    assert _CountingHandler.requests == 0


def test_a_non_http_scheme_is_refused():
    """A file URL is refused rather than read from disk."""
    with pytest.raises(server.ReadError, match='only http and https'):
        server.fetch('file:///etc/passwd')


def test_a_compressed_body_that_inflates_past_the_limit_is_refused(monkeypatch):
    """A small gzip body that would inflate beyond the download limit is refused."""
    monkeypatch.setattr(server, 'MAX_DOWNLOAD_BYTES', 1000)
    bomb = gzip.compress(b'\0' * 100_000)
    with pytest.raises(server.ReadError, match='inflates to more than'):
        server.decompress('https://example.org/a', bomb, 'gzip')


def _minimal_pdf(*sentences):
    """A PDF with one page per sentence, each page showing its sentence in Helvetica."""
    font, kids, page_objects = 3 + 2 * len(sentences), [], []
    for index, sentence in enumerate(sentences):
        stream = f'BT /F1 12 Tf 72 712 Td ({sentence}) Tj ET'.encode()
        kids.append(f'{3 + 2 * index} 0 R')
        page_objects += [
            f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {4 + 2 * index} 0 R '
            f'/Resources << /Font << /F1 {font} 0 R >> >> >>'.encode(),
            b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream',
        ]
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {len(sentences)} >>'.encode(),
        *page_objects,
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    ]
    pdf, offsets = b'%PDF-1.4\n', []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f'{number} 0 obj\n'.encode() + body + b'\nendobj\n'
    xref = len(pdf)
    pdf += f'xref\n0 {len(objects) + 1}\n0000000000 65535 f \n'.encode()
    pdf += b''.join(f'{offset:010d} 00000 n \n'.encode() for offset in offsets)
    pdf += f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF'.encode()
    return pdf


def test_a_pdf_reads_as_its_text_page_by_page():
    """A PDF, recognized by its bytes even with a generic content type, reads as page text."""
    document = server.to_document('https://example.org/paper.pdf', 'application/octet-stream',
                                  _minimal_pdf('Held-out gains were smaller'))
    assert document.kind == 'PDF'
    assert document.text.startswith('[page 1]')
    assert 'Held-out gains were smaller' in document.text


def test_an_unsupported_content_type_is_refused():
    """A binary that is neither HTML, PDF nor text fails with the type named."""
    with pytest.raises(server.ReadError, match='image/png'):
        server.to_document('https://example.org/a.png', 'image/png', b'\x89PNG')


def test_the_protocol_lists_the_tool_and_returns_a_failed_read_as_a_tool_error():
    """An MCP client sees the read_page tool, and a refused URL comes back as an error result."""
    reader = server.Reader()
    initialized = server.handle(reader, {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
                                         'params': {'protocolVersion': '2025-06-18'}})
    assert initialized['result']['protocolVersion'] == '2025-06-18'
    assert server.handle(reader, {'jsonrpc': '2.0', 'method': 'notifications/initialized'}) is None
    listed = server.handle(reader, {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})
    assert [tool['name'] for tool in listed['result']['tools']] == ['read_page']
    called = server.handle(reader, {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {
        'name': 'read_page', 'arguments': {'url': 'file:///etc/passwd'}}})
    assert called['result']['isError'] is True
    unknown = server.handle(reader, {'jsonrpc': '2.0', 'id': 4, 'method': 'resources/list'})
    assert unknown['error']['code'] == -32601


def test_a_charset_given_only_in_the_http_header_decodes_the_page():
    """A UTF-8 page that declares its encoding only in Content-Type reads without mojibake."""
    document = server.to_document('https://example.org/a', 'text/html; charset="utf-8"',
                                  '<html><body><p>Café — résumé</p></body></html>'.encode())
    assert 'Café — résumé' in document.text


def test_text_outside_the_main_element_is_kept():
    """References after a dominant <main> still reach the reader: a full read drops nothing."""
    body = ('<html><body><main><p>' + 'Finding. ' * 80 + '</p></main>'
            '<section><h2>References</h2><p>Smith 2026, Agents.</p></section></body></html>')
    text = server.html_to_text(body.encode())
    assert 'References' in text and 'Smith 2026, Agents.' in text


def test_deeply_nested_markup_keeps_the_text_after_it():
    """Nesting past the parser's default 255 levels does not silently drop the rest of the page."""
    body = b'<html><body><p>before</p>' + b'<div>' * 300 + b'x' + b'</div>' * 300
    text = server.html_to_text(body + b'<p>after</p></body></html>')
    assert 'before' in text and 'after' in text


def test_nesting_past_what_can_be_parsed_is_an_error_not_a_short_read():
    """A page nested too deep to parse whole fails instead of returning part of it as the whole."""
    body = b'<html><body>' + b'<div>' * 3000 + b'x' + b'</div>' * 3000
    body += b'<p>after</p></body></html>'
    with pytest.raises(server.ReadError, match='nested'):
        server.html_to_text(body)


def test_preformatted_text_keeps_its_indentation():
    """Code in a <pre> block comes back with its leading spaces, word for word."""
    text = server.html_to_text(b'<html><body><pre>def f():\n    return 1\n</pre></body></html>')
    assert 'def f():\n    return 1' in text


def test_a_chunk_of_multibyte_text_stays_under_the_inline_size():
    """A chunk of non-ASCII text stays under the byte size the coding agent shows a caller inline."""
    text = 'Ω' * 60_000
    reader = server.Reader(fetcher=serving('text/plain; charset=utf-8', text.encode()))
    body = reader.read('https://example.org/greek', 0).split('----\n', 1)[1]
    assert len(body.encode()) <= server.CHUNK_BYTES


@pytest.mark.parametrize('address, public', [
    ('8.8.8.8', True), ('2606:4700:4700::1111', True), ('64:ff9b::808:808', True),
    ('64:ff9b::a00:1', False), ('10.0.0.1', False), ('::ffff:127.0.0.1', False)])
def test_only_public_addresses_count_as_public(address, public):
    """A NAT64 address counts as public only when the IPv4 address it reaches is public."""
    assert server.is_public(ipaddress.ip_address(address)) is public


def test_a_url_with_non_ascii_characters_is_read_not_crashed(local_server_port):
    """A non-ASCII path is encoded and the request proceeds (here, to the local-address refusal)."""
    with pytest.raises(server.ReadError, match='not a public internet address'):
        server.fetch(f'http://localhost:{local_server_port}/Gödel')


@pytest.mark.parametrize('content_type, body', [
    ('text/html', b''), ('text/plain; charset=foo-bar', b'text'),
    ('application/pdf', b'%PDF-1.4 x')])
def test_content_that_cannot_be_converted_is_a_read_error(content_type, body):
    """An empty page, an unknown charset or a broken PDF fails as a read error naming the source."""
    reader = server.Reader(fetcher=serving(content_type, body))
    with pytest.raises(server.ReadError, match='example.org'):
        reader.read('https://example.org/a', 0)


class _TruncatingHandler(_QuietHandler):
    def do_GET(self):  # pylint: disable=invalid-name
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', '1000')
        self.end_headers()
        self.wfile.write(b'Only a prefix')
        self.close_connection = True


def test_a_body_shorter_than_its_declared_length_is_an_error(monkeypatch, serve):
    """A response cut off before its Content-Length is refused, not served as the whole page."""
    monkeypatch.setattr(server, 'is_public', every_address_is_public)
    port = serve(_TruncatingHandler)
    with pytest.raises(server.ReadError, match='ended'):
        server.fetch(f'http://127.0.0.1:{port}/')


def test_a_pdf_without_a_text_layer_is_an_error_not_a_full_read():
    """A scanned PDF, whose pages hold no text, fails instead of reading as bare page markers."""
    reader = server.Reader(fetcher=serving('application/pdf', _minimal_pdf('')))
    with pytest.raises(server.ReadError, match='no readable text'):
        reader.read('https://example.org/scan.pdf', 0)


def test_a_compressed_body_cut_off_before_its_end_is_an_error():
    """A gzip body missing its last bytes is refused, so a cut-off page never reads as whole."""
    cut_off = gzip.compress(b'The whole text of the page. ' * 100)[:-12]
    with pytest.raises(server.ReadError, match='ended'):
        server.decompress('https://example.org/a', cut_off, 'gzip')


def test_a_complete_compressed_body_inflates_to_its_text():
    """A whole gzip body passes the completeness checks and inflates to the original bytes."""
    page = b'The whole text of the page. ' * 100
    assert server.decompress('https://example.org/a', gzip.compress(page), 'gzip') == page


def test_a_compressed_body_with_a_second_member_is_an_error():
    """A gzip body holding more than one member is refused rather than read as its first part."""
    body = gzip.compress(b'First part. ') + gzip.compress(b'Second part.')
    with pytest.raises(server.ReadError, match='after the end'):
        server.decompress('https://example.org/a', body, 'gzip')


def test_a_pdf_page_without_a_text_layer_is_marked_and_never_called_read_whole():
    """A scanned page after a text cover is marked, and the end says its text was not returned."""
    pdf = _minimal_pdf('Downloaded from a library', '')
    reader = server.Reader(fetcher=serving('application/pdf', pdf))
    chunk = reader.read('https://example.org/scan.pdf', 0)
    assert 'Downloaded from a library' in chunk
    header = chunk.split('----', 1)[0]
    assert '[page 2: no extractable text' in chunk
    assert 'the text of 1 of its pages was not returned' in header
    assert 'whole text has been returned' not in header


def test_math_stored_in_a_mathjax_script_keeps_its_latex():
    """Equations a page keeps in MathJax script tags come back as their LaTeX, not dropped."""
    text = server.html_to_text(
        b'<html><body><p>Loss is <script type="math/tex">\\sum_i x_i</script>.</p>'
        b'<script type="math/tex; mode=display">E = mc^2</script>'
        b'<script>var counter = 1;</script></body></html>')
    assert '\\sum_i x_i' in text and 'E = mc^2' in text
    assert 'counter' not in text


class _EncodedHandler(_QuietHandler):
    def do_GET(self):  # pylint: disable=invalid-name
        encoding = self.path.strip('/')
        plain = b'Page text.'
        body = {'x-gzip': gzip.compress(plain), 'x-deflate': zlib.compress(plain), 'none': plain,
                'unencoded': plain}.get(encoding, b'\x1b\x00not text')
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        if encoding != 'unencoded':
            self.send_header('Content-Encoding', encoding)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def test_a_body_in_an_encoding_the_reader_cannot_decode_is_an_error(monkeypatch, serve):
    """An unknown coding is refused; aliases decode, and none or no header at all is plain."""
    monkeypatch.setattr(server, 'is_public', every_address_is_public)
    port = serve(_EncodedHandler)
    for unknown in ('br', 'x-unknown'):
        with pytest.raises(server.ReadError, match=f'encoded as {unknown}'):
            server.fetch(f'http://127.0.0.1:{port}/{unknown}')
    for encoding in ('x-gzip', 'x-deflate', 'none', 'unencoded'):
        assert server.fetch(f'http://127.0.0.1:{port}/{encoding}')[2] == b'Page text.'


def test_button_text_is_kept_apart_from_its_neighbors_and_out_of_code():
    """An accordion keeps its questions, tab labels stay apart, and code skips its copy button."""
    text = server.html_to_text(
        b'<html><body><h2><button class="accordion-button">Is my data stored in the EU?'
        b'</button></h2><div class="accordion-body">Yes, in Frankfurt.</div>'
        b'<button>Python</button><button>JavaScript</button>'
        b'<pre><button class="copy">Copy</button><code>def f():\n    return 1</code></pre>'
        b'</body></html>')
    assert 'Is my data stored in the EU?' in text and 'Yes, in Frankfurt.' in text
    assert 'PythonJavaScript' not in text
    assert 'def f():\n    return 1' in text and 'Copy' not in text
