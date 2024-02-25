from flask import Flask, jsonify, request
import jwt
from datetime import datetime, timedelta
import cryptography

app = Flask(__name__)

# Dictionary to store keys with 'kid' as key
keys = {}

# Function to generate RSA keys
def generate_rsa_keys(kid):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Generate public key
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Associate a Key ID (kid) and expiry timestamp with each key
    expiry = datetime.now() + timedelta(days=90)  # Example: Key expires after 90 days
    keys[kid] = {
        "private_key": private_pem,
        "public_key": public_pem,
        "expiry": expiry
    }

# Example key generation for initial setup
generate_rsa_keys("kid1")

@app.route("/jwks", methods=["GET"])
def get_jwks():
    # Filter and serve keys that have not expired
    valid_keys = {kid: key_info["public_key"].decode() for kid, key_info in keys.items() if key_info["expiry"] > datetime.now()}
    return jsonify(valid_keys)

@app.route("/auth", methods=["POST"])
def auth():
    expired = request.args.get("expired", "false").lower() == "true"
    kid = "kid1"  # Use the first key for simplicity; in real-world, select based on some logic
    
    # Issue JWT
    if expired and kid in keys:  # Handle expired keys differently if needed
        key_info = keys[kid]  # Example; in real-world, you might have a different handling
        # Your logic to issue a JWT with the expired key
    else:
        key_info = keys[kid]
    
    # Generate JWT
    payload = {"sub": "1234567890", "name": "John Doe", "iat": datetime.now()}
    token = jwt.encode(payload, key_info["private_key"], algorithm="RS256", headers={"kid": kid})
    
    return jsonify({"token": token})

if __name__ == "__main__":
    app.run(port=8080)
