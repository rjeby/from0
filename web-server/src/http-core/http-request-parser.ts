import { HTTPConnection } from "./http-connection";
import { HTTP_TRIE, METHOD_TRIE } from "../data-structures/trie";
import { HTTPError } from "./http-error";
import { HTTPRequest } from "./http-request";

const MAX_HEADER_SIZE = 8 * 1024;
const MAX_CONTENT_SIZE = 10 * 1024 * 1024;

export class HTTPRequestParser {
  connection: HTTPConnection;
  requestHeaderSize: number;
  requestBodySize: number;

  constructor(connection: HTTPConnection) {
    this.connection = connection;
    this.requestHeaderSize = 0;
    this.requestBodySize = 0;
  }

  consume() {
    if (this.requestHeaderSize >= MAX_HEADER_SIZE) {
      throw new HTTPError(431, "Request Header Fields Too Large");
    }
    this.connection.consume();
    this.requestHeaderSize++;
  }

  unconsume() {
    this.connection.unconsume();
    this.requestHeaderSize--;
  }

  isHEXDIG(b: number): boolean {
    return (b >= 0x30 && b <= 0x39) || (b >= 0x41 && b <= 0x46) || (b >= 0x61 && b <= 0x66);
  }

  isDIGIT(b: number) {
    return b >= 0x30 && b <= 0x39;
  }

  isALPHA(b: number) {
    return (b >= 0x61 && b <= 0x7a) || (b >= 0x41 && b <= 0x5a);
  }

  isUnreserved(b: number) {
    return this.isALPHA(b) || this.isDIGIT(b) || b === 0x2d || b === 0x2e || b === 0x5f || b === 0x7e;
  }

  isSubDelims(b: number) {
    return b === 0x21 || b === 0x24 || b === 0x26 || b === 0x27 || b === 0x28 || b === 0x29 || b === 0x2a || b === 0x2b || b === 0x2c || b === 0x3b || b === 0x3d;
  }

  isTChar(b: number) {
    return this.isDIGIT(b) || this.isALPHA(b) || b === 0x21 || b === 0x23 || b === 0x24 || b === 0x25 || b === 0x26 || b === 0x27 || b === 0x2a || b === 0x2b || b === 0x2d || b === 0x2e || b === 0x5e || b === 0x5f || b === 0x60 || b === 0x7c || b === 0x7e;
  }

  isVCHAR(b: number) {
    return b >= 0x21 && b <= 0x7e;
  }

  isObsText(b: number) {
    return b >= 0x80 && b <= 0xff;
  }

  isFieldVchar(b: number) {
    return this.isVCHAR(b) || this.isObsText(b);
  }

  async parseRequest() {
    const [method, uri, version, headers] = await this.parseRequestHeader();
    this.connection.skip();
    const body = await this.parseBody(method, headers);
    this.connection.skip();
    console.log(body.toString(), "###");

    return new HTTPRequest(method, uri, version, headers, body);
  }

  async parseBody(method: string, header: Map<string, string>) {
    if (method === "GET") {
      return Buffer.from("");
    }

    const contentLength = Number(header.get("content-length"));
    const transferEncoding = header.get("transfer-encoding");

    if (contentLength > 0) {
      return await this.parseBodyByContentLength(contentLength);
    } else if (transferEncoding === "chunked") {
      return await this.parseChunkedBody();
    } else {
      return await this.parseFullConnection();
    }
  }

  async parseFullConnection() {
    const body = Buffer.from(await this.connection.readAllConnection());
    this.connection.consume(body.length);
    return body;
  }

  async parseChunkedBody() {
    while (true) {
      const chunkLength = Number(await this.parseChunkLength());
      if (!chunkLength) {
        await this.parseCRLF();
        await this.parseCRLF();
        this.requestBodySize += 4;
        return Buffer.from(this.connection.buffer.readAll());
      }
      await this.parseCRLF();
      await this.connection.readBytes(chunkLength);
      this.connection.consume(chunkLength);
      await this.parseCRLF();
      this.requestBodySize += 4;
    }
  }

  async parseChunkLength() {
    let value = 0;
    const byte = await this.connection.readByte();
    if (!this.isDIGIT(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    value = value * 10 + (byte - 0x30);
    this.connection.consume();
    while (true) {
      const byte = await this.connection.readByte();
      if (!this.isDIGIT(byte)) {
        this.requestBodySize = this.requestBodySize + value;
        return value;
      }
      value = value * 10 + (byte - 0x30);
      if (value + this.requestBodySize > MAX_CONTENT_SIZE) {
        throw new HTTPError(413, "Payload Too Large");
      }
      this.connection.consume();
    }
  }

  async parseBodyByContentLength(contentLength: number) {
    await this.connection.readBytes(contentLength);
    this.connection.consume(contentLength);
    return Buffer.from(this.connection.buffer.readAll());
  }

  async parseRequestHeader(): Promise<[string, string, string, Map<string, string>]> {
    const method = await this.parseMethod();
    await this.parseSP();
    const uri = await this.parseURI();
    await this.parseSP();
    const version = await this.parseVersion();
    await this.parseCRLF();
    const headers = await this.parseHeaders();
    await this.parseCRLF();
    return [method, uri, version, headers];
  }

  async parseSP() {
    const byte = await this.connection.readByte();
    if (byte !== 0x20) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
  }

  async parseCRLF() {
    const fb = await this.connection.readByte();
    if (fb !== 0x0d) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
    const sb = await this.connection.readByte();
    if (sb !== 0x0a) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
  }

  async parseUnreserved() {
    const byte = await this.connection.readByte();
    if (!this.isUnreserved(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
  }

  async parsePctEncoded() {
    const byte = await this.connection.readByte();
    if (byte !== 0x25) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
    await this.parseHEXDIG();
    await this.parseHEXDIG();
  }

  async parseHEXDIG() {
    const byte = await this.connection.readByte();
    if (!this.isHEXDIG(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
  }

  async parseSubDelims() {
    const c = await this.connection.readByte();
    if (!this.isSubDelims(c)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
  }

  async parsePchar() {
    const byte = await this.connection.readByte();
    if (this.isUnreserved(byte)) {
      await this.parseUnreserved();
    } else if (this.isSubDelims(byte)) {
      await this.parseSubDelims();
    } else if (byte === 0x3a || byte === 0x40) {
      this.consume();
    } else if (byte === 0x25) {
      await this.parsePctEncoded();
    } else {
      throw new HTTPError(400, "Bad Request");
    }
  }

  async parseSegement() {
    while (true) {
      const byte = await this.connection.readByte();
      if (!this.isUnreserved(byte) && !this.isSubDelims(byte) && byte !== 0x25 && byte !== 0x3a && byte !== 0x40) {
        return;
      }
      await this.parsePchar();
    }
  }

  async parseQuery() {
    while (true) {
      const byte = await this.connection.readByte();
      if (!this.isUnreserved(byte) && !this.isSubDelims(byte) && byte !== 0x25 && byte !== 0x2f && byte !== 0x2f) {
        return;
      }
      await this.parsePchar();
    }
  }

  async parseAbsolutePath() {
    const byte = await this.connection.readByte();
    if (byte !== 0x2f) {
      throw new HTTPError(400, "Bad Request");
    }

    this.consume();
    await this.parseSegement();
    while (true) {
      const byte = await this.connection.readByte();
      if (byte !== 0x2f) {
        return;
      }
      this.consume();
      await this.parseSegement();
    }
  }

  async parseURI() {
    const beg = this.connection.buffer.beg;
    await this.parseAbsolutePath();
    const end = this.connection.buffer.beg;
    const byte = await this.connection.readByte();
    if (byte === 0x3f) {
      this.consume();
      await this.parseQuery();
    }
    return this.connection.buffer.subarray(beg, end).toString("ascii");
  }

  async parseMethod() {
    const method: string[] = [];
    let current = METHOD_TRIE.root;
    while (true) {
      const byte = await this.connection.readByte();
      if (byte === 0x20 && !current.isWord) {
        throw new HTTPError(400, "Bad Request");
      }
      if (byte === 0x20) {
        return method.join("");
      }
      if (!current.children.has(byte)) {
        throw new HTTPError(400, "Bad Request");
      }
      method.push(String.fromCharCode(byte));
      current = current.children.get(byte)!;
      this.consume();
    }
  }

  async parseVersion() {
    let current = HTTP_TRIE.root;
    while (true) {
      const byte = await this.connection.readByte();
      if (byte === 0x2f && current.isWord) {
        break;
      }
      if (!current.children.has(byte)) {
        throw new HTTPError(400, "Bad Request");
      }
      current = current.children.get(byte)!;
      this.consume();
    }

    const slash = await this.connection.readByte();
    if (slash !== 0x2f) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();

    const lv = await this.connection.readByte();
    if (lv !== 0x31) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
    const dot = await this.connection.readByte();
    if (dot !== 0x2e) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();

    const rv = await this.connection.readByte();
    if (rv !== 0x31 && rv !== 0x30) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
    return rv === 0x30 ? "1.0" : "1.1";
  }

  async parseFieldLine() {
    const fieldNameBeg = this.connection.buffer.beg;
    await this.parseFieldName();
    const fieldNameEnd = this.connection.buffer.beg;
    const fieldName = this.connection.buffer.subarray(fieldNameBeg, fieldNameEnd).toString("latin1").toLowerCase();
    const sc = await this.connection.readByte();
    if (sc !== 0x3a) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
    await this.parseOWS();
    const fieldValueBeg = this.connection.buffer.beg;
    if (fieldName === "content-length") {
      await this.parseContentLength();
    } else {
      await this.parseFieldValue();
    }
    const fieldValueEnd = this.connection.buffer.beg;
    await this.parseOWS();
    return [fieldName, this.connection.buffer.subarray(fieldValueBeg, fieldValueEnd).toString("latin1")];
  }

  async parseToken() {
    await this.parseTchar();
    while (true) {
      const byte = await this.connection.readByte();
      if (!this.isTChar(byte)) {
        return;
      }
      await this.parseTchar();
    }
  }

  async parseFieldName() {
    await this.parseToken();
  }

  async parseFieldValue() {
    while (true) {
      const byte = await this.connection.readByte();
      if (!this.isFieldVchar(byte)) {
        return;
      }
      await this.parseFieldContent();
    }
  }

  async parseFieldContent() {
    await this.parseFieldVchar();
    while (true) {
      const byte = await this.connection.readByte();
      if (byte !== 0x20 && byte !== 0x09 && !this.isFieldVchar(byte)) {
        break;
      }
      this.consume();
    }
    while (true) {
      this.unconsume();
      const byte = await this.connection.readByte();
      if (this.isFieldVchar(byte)) {
        this.consume();
        return;
      }
    }
  }

  async parseFieldVchar() {
    const byte = await this.connection.readByte();
    if (!this.isFieldVchar(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
  }

  async parseTchar() {
    const byte = await this.connection.readByte();
    if (!this.isTChar(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.consume();
  }

  async parseOWS() {
    while (true) {
      const byte = await this.connection.readByte();
      if (byte !== 0x20 && byte !== 0x09) {
        return;
      }
      this.consume();
    }
  }

  async parseContentLength() {
    let value = 0;
    const byte = await this.connection.readByte();
    if (!this.isDIGIT(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    value = value * 10 + (byte - 0x30);
    this.consume();
    while (true) {
      const byte = await this.connection.readByte();
      if (!this.isDIGIT(byte)) {
        return;
      }
      value = value * 10 + (byte - 0x30);
      if (value > MAX_CONTENT_SIZE) {
        throw new HTTPError(413, "Payload Too Large");
      }
      this.consume();
    }
  }

  async parseHeaders() {
    const headers: Map<string, string> = new Map();
    while (true) {
      const byte = await this.connection.readByte();
      if (!this.isTChar(byte)) {
        break;
      }
      const [fieldName, fieldValue] = await this.parseFieldLine();
      if (headers.has(fieldName) && (fieldName === "host" || fieldName === "content-length")) {
        throw new HTTPError(400, "Bad Request");
      }

      headers.set(fieldName, fieldValue);
      await this.parseCRLF();
    }

    if (!headers.has("host")) {
      throw new HTTPError(400, "Bad Request");
    }

    return headers;
  }
}
