from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import datetime
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from urllib.parse import urlparse, parse_qs
import base64
import json

# Configuration
DB_FILE = "totally_not_my_privateKeys.db"
HOST_NAME = "localhost"
SERVER_PORT = 8080

# Database setup and key storage
def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS keys(
        kid INTEGER PRIMARY KEY AUTOINCREMENT,
        key BLOB NOT NULL,
        exp INTEGER NOT NULL
    )""")
    conn.commit()
    conn.close()

def store_key(key_pem, exp):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO keys (key, exp) VALUES (?, ?)", (key_pem, exp))
    conn.commit()
    conn.close()

def generate_and_store_keys():
    valid_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    valid_pem = valid_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    valid_exp = int((datetime.datetime.utcnow() + datetime.timedelta(hours=1)).timestamp())
    store_key(valid_pem, valid_exp)

    expired_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    expired_pem = expired_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    expired_exp = int((datetime.datetime.utcnow() - datetime.timedelta(hours=1)).timestamp())
    store_key(expired_pem, expired_exp)

# Utility functions
def int_to_base64(value):
    """Convert an integer to Base64URL-encoded string."""
    return base64.urlsafe_b64encode(value.to_bytes((value.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')

def pem_to_jwk(pem):
    """Convert PEM-encoded RSA private key to JWK format."""
    private_key = serialization.load_pem_private_key(pem.encode('utf-8'), password=None, backend=default_backend())
    public_key = private_key.public_key()
    numbers = public_key.public_numbers()
    return {
        "kty": "RSA",
        "use": "sig",
        "kid": "dynamicKID",
        "alg": "RS256",
        "n": int_to_base64(numbers.n),
        "e": int_to_base64(numbers.e),
    }

# Server implementation
class MyServer(BaseHTTPRequestHandler):
    def get_key(self, expired=False):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = int(datetime.datetime.utcnow().timestamp())
        if expired:
            cursor.execute("SELECT key FROM keys WHERE exp < ? ORDER BY exp DESC LIMIT 1", (now,))
        else:
            cursor.execute("SELECT key FROM keys WHERE exp > ? ORDER BY exp ASC LIMIT 1", (now,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return None

    def do_POST(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        if parsed_path.path == "/auth":
            key_pem = self.get_key('expired' in params)
            if not key_pem:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Key not found")
                return
            
            headers = {"kid": "dynamicKID"}
            token_payload = {
                "user": "username",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            }
            encoded_jwt = jwt.encode(token_payload, key_pem, algorithm="RS256", headers=headers)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(encoded_jwt.encode('utf-8'))

    def do_GET(self):
        if self.path == "/.well-known/jwks.json":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            now = int(datetime.datetime.utcnow().timestamp())
            cursor.execute("SELECT key FROM keys WHERE exp > ?", (now,))
            rows = cursor.fetchall()
            conn.close()

            jwks = {"keys": []}
            for row in rows:
                key_pem = row[0]
                jwk = pem_to_jwk(key_pem)
                jwks["keys"].append(jwk)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(jwks).encode('utf-8'))
            return

        self.send_response(405)
        self.end_headers()

if __name__ == "__main__":
    initialize_db()
    generate_and_store_keys()

    webServer = HTTPServer((HOST_NAME, SERVER_PORT), MyServer)
    print(f"Server started http://{HOST_NAME}:{SERVER_PORT}")
    
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

