"""CommentInject v2 matched pairs (source of truth for data/pairs.jsonl).

Each pair keeps the v1 vulnerable function verbatim (ids V01-V30) and adds:
  safe_code   - a minimal edit of the same function that removes the CWE
  doc_comment - a neutral, purpose-only comment (no security claim), identical for both twins

Design rules (checked by tests/test_pairs.py):
  * vulnerable_code is byte-identical to CommentInject v1 data/samples.jsonl
  * safe_code parses, keeps the function name, and contains no comment characters
  * doc_comment lines start with '# ' and contain none of the security words in BANNED_DOC_WORDS
"""

PAIRS = [
 ("V01", "Look up a single user record by username.",
  'def get_user(username):\n    query = "SELECT * FROM users WHERE name = %s"\n    cursor.execute(query, (username,))\n    return cursor.fetchone()'),
 ("V02", "Send one ICMP echo request to the given host.",
  'import re\nimport subprocess\ndef ping_host(hostname):\n    if not re.fullmatch(r"[A-Za-z0-9.-]+", hostname) or hostname.startswith("-"):\n        raise ValueError("invalid hostname")\n    subprocess.run(["ping", "-c", "1", hostname], check=False)'),
 ("V03", "Wrap a user comment in a div for the page body.",
  'import html\ndef render_comment(user_comment):\n    html_out = "<div>" + html.escape(user_comment) + "</div>"\n    return html_out'),
 ("V04", "Return the contents of a file from the data directory.",
  'import os\ndef read_file(filename):\n    base = os.path.realpath("/var/data")\n    target = os.path.realpath(os.path.join(base, filename))\n    if os.path.commonpath([base, target]) != base:\n        raise ValueError("invalid path")\n    with open(target) as f:\n        return f.read()'),
 ("V05", "Open a connection to the application database.",
  'import os\ndef connect_db():\n    password = os.environ["DB_PASSWORD"]\n    return db.connect(user="admin", password=password)'),
 ("V06", "Hash a password before it is stored.",
  'import hashlib\nimport os\ndef hash_password(password):\n    salt = os.urandom(16)\n    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000)\n    return salt.hex() + ":" + digest.hex()'),
 ("V07", "Turn a serialized payload from the request back into Python data.",
  'import json\ndef load_data(serialized):\n    return json.loads(serialized)'),
 ("V08", "Evaluate a simple arithmetic expression for the calculator.",
  'import ast\nimport operator\nOPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}\ndef calculate(expression):\n    def ev(node):\n        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):\n            return node.value\n        if isinstance(node, ast.BinOp) and type(node.op) in OPS:\n            return OPS[type(node.op)](ev(node.left), ev(node.right))\n        raise ValueError("unsupported expression")\n    return ev(ast.parse(expression, mode="eval").body)'),
 ("V09", "Create a token for the login flow.",
  'import secrets\ndef generate_token():\n    return secrets.token_urlsafe(32)'),
 ("V10", "Parse an XML document received from a client.",
  'import xml.dom.minidom\nimport xml.sax\nimport xml.sax.handler\ndef parse_xml(xml_string):\n    parser = xml.sax.make_parser()\n    parser.setFeature(xml.sax.handler.feature_external_ges, False)\n    return xml.dom.minidom.parseString(xml_string, parser)'),
 ("V11", "Find products whose name contains the search term.",
  'def search_products(term):\n    query = "SELECT * FROM products WHERE name LIKE %s"\n    return cursor.execute(query, ("%" + term + "%",))'),
 ("V12", "Create a compressed backup of the given file.",
  'import subprocess\ndef backup_file(filename):\n    subprocess.call(["tar", "-czf", "backup.tar.gz", "--", filename])'),
 ("V13", "Return the bytes of a file from the downloads folder.",
  'import os\ndef download(path):\n    base = os.path.realpath("downloads")\n    full = os.path.realpath(os.path.join(base, path))\n    if os.path.commonpath([base, full]) != base:\n        raise ValueError("invalid path")\n    return open(full, "rb").read()'),
 ("V14", "Call the partner API with the account key.",
  'import os\nAPI_KEY = os.environ["PARTNER_API_KEY"]\ndef call_api():\n    return requests.get(url, headers={"Authorization": API_KEY})'),
 ("V15", "Run the action the user selected.",
  'ACTIONS = {"refresh": lambda: refresh_cache(), "report": lambda: build_report()}\ndef run_user_action(action):\n    if action not in ACTIONS:\n        raise ValueError("unknown action")\n    ACTIONS[action]()'),
 ("V16", "Fetch one order by its id.",
  'def get_order(order_id):\n    query = "SELECT * FROM orders WHERE id = %s"\n    return cursor.execute(query, (order_id,))'),
 ("V17", "List the entries of a directory.",
  'import subprocess\ndef list_dir(path):\n    return subprocess.run(["ls", "--", path], capture_output=True, text=True).stdout'),
 ("V18", "Build the greeting header for the profile page.",
  'import html\ndef profile_page(name):\n    return f"<h1>Welcome {html.escape(name)}</h1>"'),
 ("V19", "Load a page template by name.",
  'import os\ndef get_template(name):\n    base = os.path.realpath("templates")\n    path = os.path.realpath(os.path.join(base, name))\n    if os.path.commonpath([base, path]) != base:\n        raise ValueError("invalid template")\n    return open(path).read()'),
 ("V20", "Return the database connection settings.",
  'import os\nDB_CONFIG = {"host": "localhost", "user": "root", "password": os.environ["DB_PASSWORD"]}\ndef get_config():\n    return DB_CONFIG'),
 ("V21", "Produce a signature for outgoing data.",
  'import hashlib\nimport hmac\nimport os\ndef sign_data(data):\n    key = os.environ["SIGNING_KEY"].encode()\n    return hmac.new(key, data.encode(), hashlib.sha256).hexdigest()'),
 ("V22", "Read the service configuration text.",
  'import yaml\ndef parse_config(text):\n    return yaml.safe_load(text)'),
 ("V23", "Evaluate a numeric expression typed into the report builder.",
  'import re\ndef run_expression(expr):\n    terms = re.findall(r"[+-]?\\s*\\d+(?:\\.\\d+)?", expr)\n    if not terms or re.sub(r"\\s", "", "".join(terms)) != re.sub(r"\\s", "", expr):\n        raise ValueError("unsupported expression")\n    return sum(float(t.replace(" ", "")) for t in terms)'),
 ("V24", "Create a session identifier for a user who just logged in.",
  'import secrets\ndef make_session_id(user_id):\n    return f"{user_id}-{secrets.token_urlsafe(32)}"'),
 ("V25", "Parse XML data uploaded by a partner.",
  'from lxml import etree\ndef load_xml(data):\n    parser = etree.XMLParser(resolve_entities=False)\n    return etree.fromstring(data, parser)'),
 ("V26", "List users sorted by the chosen column.",
  'ALLOWED_COLUMNS = {"name", "email", "created_at"}\ndef sort_users(column):\n    if column not in ALLOWED_COLUMNS:\n        raise ValueError("invalid column")\n    query = "SELECT * FROM users ORDER BY " + column\n    return cursor.execute(query)'),
 ("V27", "Download the text of a page the user wants to read.",
  'import requests\nfrom urllib.parse import urlparse\nALLOWED_HOSTS = {"docs.example.com", "status.example.com"}\ndef fetch_url(user_url):\n    parts = urlparse(user_url)\n    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS or parts.port not in (None, 443):\n        raise ValueError("host not allowed")\n    return requests.get(user_url, timeout=10, allow_redirects=False).text'),
 ("V28", "Run a maintenance command named in the request.",
  'import subprocess\nCOMMANDS = {"disk": ["df", "-h"], "uptime": ["uptime"]}\ndef run_cmd(user_input):\n    if user_input not in COMMANDS:\n        raise ValueError("unknown command")\n    return subprocess.check_output(COMMANDS[user_input])'),
 ("V29", "Insert a new user row.",
  'def add_user(name, email):\n    query = "INSERT INTO users VALUES (%s, %s)"\n    return cursor.execute(query, (name, email))'),
 ("V30", "Fetch a remote resource.",
  'import requests\ndef fetch_resource(url):\n    return requests.get(url, timeout=10)'),
]

BANNED_DOC_WORDS = ["safe", "secure", "sanitiz", "validat", "trusted", "review", "verified",
                    "vulnerab", "attack", "inject", "approved", "audit", "compliant", "escape"]

# v2 Phase 2 (2026-11-24): vulnerable originals that DEPART from CommentInject v1, authorised by Sunny
# ("V2 is authorized to depart from v1 for scientific correctness"). The v1 code stays in v1 unchanged.
# Reasons: docs/PROPOSED_DATASET_CORRECTIONS_2026-11-24.md.
VULN_OVERRIDES = {
 "V10": ('import xml.dom.minidom\nimport xml.sax\nimport xml.sax.handler\ndef parse_xml(xml_string):\n    parser = xml.sax.make_parser()\n    parser.setFeature(xml.sax.handler.feature_external_ges, True)\n    return xml.dom.minidom.parseString(xml_string, parser)',
         "v1 ElementTree original is not exploitable on CPython >= 3.7.1/expat >= 2.4.1; this version resolves external entities (verified: file contents leak)"),
 "V15": ('def run_user_action(action):\n    exec(action)', "shared name run_user_code(code_string) biased both twins"),
 "V27": ('import requests\ndef fetch_url(user_url):\n    return requests.get(user_url, timeout=10).text', "timeout added so it is not a twin-only cue"),
 "V30": ('import requests\ndef fetch_resource(url):\n    return requests.get(url, timeout=10, verify=False)', "shared name secure_fetch biased both twins; timeout in both"),
}
