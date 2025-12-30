# HTTP Server

A **minimal HTTP/1.1 echo server** built from scratch using **Node.js**.  
The server listens for incoming HTTP requests (POST /echo) and responds by echoing back the request body.

This project is intentionally simple and focuses on the basics of the HTTP/1.1 protocol.

---

## How to Start the Server

### 1. Clone repository

```bash
git clone <repo-url>
cd web-server
```

### 2. Install dependencies

Install packages:

```bash
npm install
```

### 3. Run the project

The server will start on localhost:1234.

```bash
npm run start
```

### 4. Send a request

Use any HTTP client (for example, curl) to send a request to the server.

```bash
curl -X POST http://localhost:1234/echo -d "Hello, world!"
```

If the request is valid, the server will respond with the same body that was sent in the request.
