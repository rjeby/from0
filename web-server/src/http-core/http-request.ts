import { SecWebSocketKeyParser } from "../ws-core/sec-ws-key-praser";

export class HTTPRequest {
  method: string;
  uri: string;
  version: string;
  header: Map<string, string>;
  body: Buffer;

  constructor(method: string, uri: string, version: string, header: Map<string, string>, body: Buffer) {
    this.method = method;
    this.uri = uri;
    this.version = version;
    this.header = header;
    this.body = body;
  }

  switchProtocol() {
    if (!this.header.has("upgrade") || !(this.header.has("connection") || !this.header.has("Sec-WebSocket-key"))) {
      return false;
    }
    const upgrade = this.header.get("upgrade")!.toLowerCase();
    const connection = this.header.get("connection")!.toLowerCase();
    const secWebSocketKey = this.header.get("sec-websocket-key")!.toLowerCase();
    return upgrade === "websocket" && connection === "upgrade" && new SecWebSocketKeyParser(secWebSocketKey).parseSebWebSocketKey();
  }

  getField(field: string) {
    return this.header.get(field);
  }
}
