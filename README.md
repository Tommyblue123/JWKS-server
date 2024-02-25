# JWKS-server

This project implements a basic JSON Web Key Set (JWKS) server using Flask, a Python web framework. The server provides public keys with unique identifiers (KIDs) for verifying JSON Web Tokens (JWTs). It includes features such as key expiry, an authentication endpoint, and the ability to issue JWTs with expired keys based on a query parameter.

## Features

- **RSA Key Pair Generation**: Generates RSA key pairs for signing and verifying tokens.
- **Key Expiry**: Associates each key with an expiry timestamp to enhance security.
- **JWKS Endpoint**: A RESTful endpoint that serves public keys in JWKS format.
- **Authentication Endpoint**: Issues JWTs upon POST requests, supporting an optional `expired` query parameter to test JWT issuance with expired keys.


## Getting Started

### Prerequisites

- Python 3.6 or later
- Flask
- PyJWT
- cryptography

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Tommyblue123/JWKS-server.git
   cd JWKS-server

### Create and activate a virtual environment:
 ```bash
  python -m venv venv
  source venv/bin/activate
```

### Install the required packages:
 ```bash
  pip install Flask PyJWT cryptography
```


## Running the Server
 1. Start the server by running:
   ```bash
    python app.py
   ```
    
 2. The server will start on http://localhost:8080. You can access the JWKS endpoint at http://localhost:8080/jwks and the authentication endpoint at http://localhost:8080/auth.



## Usage

### JWKS Endpoint
     GET /jwks: Retrieves the current set of public keys in JWKS format.

### Authentication Endpoint
     POST /auth: Issues a JWT.
     Optional query parameter: expired (set to true to issue a JWT signed with an expired key).



  ## Testing

  To run the test suite and ensure the server behaves as expected:
  ```bash
    python -m unittest discover
```



![Screenshot (698)](https://github.com/Tommyblue123/JWKS-server/assets/98850127/38a302e6-31b3-4932-9c0c-5578b977d14d)
