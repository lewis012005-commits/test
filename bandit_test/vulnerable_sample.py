"""Deliberately insecure sample for exercising Bandit.

DO NOT import or run this in anything real. Every function below contains
a known-bad pattern on purpose so a scanner has something to find. A few
safe functions are mixed in so triage has false-positive decoys to judge.
"""
import hashlib
import os
import pickle
import random
import sqlite3
import subprocess
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

import requests
import yaml
from flask import Flask

app = Flask(__name__)

# B105: hardcoded password string
DB_PASSWORD = "hunter2"
API_TOKEN = "not-a-real-token-1234"


def run_user_command(cmd):
    # B602: subprocess with shell=True on user input
    return subprocess.call(cmd, shell=True)


def run_os_command(filename):
    # B605: os.system with string concatenation
    os.system("cat " + filename)


def evaluate_expression(expr):
    # B307: eval on untrusted input
    return eval(expr)


def execute_snippet(code):
    # B102: exec on untrusted input
    exec(code)


def load_session(blob):
    # B301: unpickling untrusted data
    return pickle.loads(blob)


def load_config(text):
    # B506: yaml.load without SafeLoader
    return yaml.load(text, Loader=yaml.Loader)


def hash_password(password):
    # B324: weak hash for passwords
    return hashlib.md5(password.encode()).hexdigest()


def make_reset_token():
    # B311: non-cryptographic RNG for a security token
    return str(random.randint(100000, 999999))


def find_user(username):
    # B608: SQL built by string formatting
    conn = sqlite3.connect("users.db")
    query = "SELECT * FROM users WHERE name = '%s'" % username
    return conn.execute(query).fetchall()


def fetch_insecure(url):
    # B501 + B113: TLS verification off, no timeout
    return requests.get(url, verify=False)


def open_any_url(url):
    # B310: urlopen accepts file:// and other schemes
    return urllib.request.urlopen(url).read()


def parse_xml(data):
    # B314: stdlib XML parser on untrusted input
    return ET.fromstring(data)


def write_temp(data):
    # B108 + B306: hardcoded /tmp path and race-prone mktemp
    path = tempfile.mktemp()
    with open("/tmp/app_cache.txt", "w") as f:
        f.write(data)
    return path


def check_admin(user):
    # B101: assert used for access control (stripped under -O)
    assert user.get("is_admin"), "not an admin"
    return True


# --- Safe decoys: Bandit may still flag some of these ---

def run_fixed_command():
    # Fixed argument list, no shell. Bandit still reports B603 as low.
    return subprocess.run(["ls", "-l"], check=False, timeout=10)


def shuffle_display_order(items):
    # random is fine here: nothing security-relevant. Still B311.
    random.shuffle(items)
    return items


def find_user_safe(username):
    conn = sqlite3.connect("users.db")
    return conn.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchall()


if __name__ == "__main__":
    # B201 + B104: debug mode on, bound to all interfaces
    app.run(host="0.0.0.0", debug=True)
