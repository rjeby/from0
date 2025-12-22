import { HTTPConnection, HTTPError } from "./tcp-server";
import { HTTP_TRIE, METHOD_TRIE } from "./trie";

export class HTTPRequestParser {
  connection: HTTPConnection;
  constructor(connection: HTTPConnection) {
    this.connection = connection;
  }

  async parseRequest() {
    const method = await new HTTPMethodParser(this.connection).parseMethod();
    await this.parseSP();
    const uri = await new HTTPUriParser(this.connection).parseURI();
    await this.parseSP();
    const version = await new HTTPVersionParser(this.connection).parseVersion();
    await this.parseCRLF();
    const headers = await new HTTPHeadersParser(this.connection).parseHeaders();
    await this.parseCRLF();
    console.log("GOOD");
  }

  async parseSP() {
    const byte = await this.connection.readByte();
    if (byte !== 0x20) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
  }

  async parseCRLF() {
    const fb = await this.connection.readByte();
    if (fb !== 0x0d) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
    const sb = await this.connection.readByte();
    if (sb !== 0x0a) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
  }
}
class HTTPUriParser {
  connection: HTTPConnection;
  constructor(connection: HTTPConnection) {
    this.connection = connection;
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

  async parseUnreserved() {
    const byte = await this.connection.readByte();
    if (!this.isUnreserved(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
  }

  async parsePctEncoded() {
    const byte = await this.connection.readByte();
    if (byte !== 0x25) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
    await this.parseHEXDIG();
    await this.parseHEXDIG();
  }

  async parseHEXDIG() {
    const byte = await this.connection.readByte();
    if (!this.isHEXDIG(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
  }

  async parseSubDelims() {
    const c = await this.connection.readByte();
    if (!this.isSubDelims(c)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
  }

  async parsePchar() {
    const byte = await this.connection.readByte();
    if (this.isUnreserved(byte)) {
      await this.parseUnreserved();
    } else if (this.isSubDelims(byte)) {
      await this.parseSubDelims();
    } else if (byte === 0x3a || byte === 0x40) {
      this.connection.consume();
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

    this.connection.consume();
    await this.parseSegement();
    while (true) {
      const byte = await this.connection.readByte();
      if (byte !== 0x2f) {
        return;
      }
      this.connection.consume();
      await this.parseSegement();
    }
  }

  async parseURI() {
    await this.parseAbsolutePath();
    const byte = await this.connection.readByte();
    if (byte === 0x3f) {
      this.connection.consume();
      await this.parseQuery();
    }
  }
}

class HTTPMethodParser {
  connection: HTTPConnection;
  constructor(connection: HTTPConnection) {
    this.connection = connection;
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
      this.connection.consume();
    }
  }
}

class HTTPVersionParser {
  connection: HTTPConnection;
  constructor(connection: HTTPConnection) {
    this.connection = connection;
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
      this.connection.consume();
    }

    const slash = await this.connection.readByte();
    if (slash !== 0x2f) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();

    const lv = await this.connection.readByte();
    if (lv !== 0x31) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
    const dot = await this.connection.readByte();
    if (dot !== 0x2e) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();

    const rv = await this.connection.readByte();
    if (rv !== 0x31 && rv !== 0x30) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
    return rv === 0x30 ? "1.0" : "1.1";
  }
}

class HTTPHeadersParser {
  connection: HTTPConnection;
  constructor(connection: HTTPConnection) {
    this.connection = connection;
  }

  isDIGIT(b: number) {
    return b >= 0x30 && b <= 0x39;
  }

  isALPHA(b: number) {
    return (b >= 0x61 && b <= 0x7a) || (b >= 0x41 && b <= 0x5a);
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

  async parseFieldLine() {
    await this.parseFieldName();
    const sc = await this.connection.readByte();
    if (sc !== 0x3a) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
    await this.parseOWS();
    await this.parseFieldValue();
    await this.parseOWS();
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
        // Move Buffer Pointer to the last valid FieldVchar
        break;
      }
      this.connection.consume();
    }
    while (true) {
      this.connection.unconsume();
      const byte = await this.connection.readByte();
      if (this.isFieldVchar(byte)) {
        this.connection.consume();
        return;
      }
    }
  }

  async parseFieldVchar() {
    const byte = await this.connection.readByte();
    if (!this.isFieldVchar(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
  }

  async parseTchar() {
    const byte = await this.connection.readByte();
    if (!this.isTChar(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
  }

  async parseOWS() {
    while (true) {
      const byte = await this.connection.readByte();
      if (byte !== 0x20 && byte !== 0x09) {
        return;
      }
      this.connection.consume();
    }
  }

  async parseCRLF() {
    const fb = await this.connection.readByte();
    if (fb !== 0x0d) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
    const sb = await this.connection.readByte();
    if (sb !== 0x0a) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume();
  }

  async parseHeaders() {
    while (true) {
      const byte = await this.connection.readByte();
      if (!this.isTChar(byte)) {
        return;
      }
      await this.parseFieldLine();
      await this.parseCRLF();
    }
  }
}
