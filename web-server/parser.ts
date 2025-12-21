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
    const byte = (await this.connection.read(1))[0];
    if (byte !== 0x20) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
  }

  async parseCRLF() {
    const fb = (await this.connection.read(1))[0];
    if (fb !== 0x0d) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
    const sb = (await this.connection.read(1))[0];
    if (sb !== 0x0a) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
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
    const byte = (await this.connection.read(1))[0];
    if (!this.isUnreserved(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
  }

  async parsePctEncoded() {
    const byte = (await this.connection.read(1))[0];
    if (byte !== 0x25) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
    await this.parseHEXDIG();
    await this.parseHEXDIG();
  }

  async parseHEXDIG() {
    const byte = (await this.connection.read(1))[0];
    if (!this.isHEXDIG(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
  }

  async parseSubDelims() {
    const c = (await this.connection.read(1))[0];
    if (!this.isSubDelims(c)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
  }

  async parsePchar() {
    const byte = (await this.connection.read(1))[0];
    if (this.isUnreserved(byte)) {
      await this.parseUnreserved();
    } else if (this.isSubDelims(byte)) {
      await this.parseSubDelims();
    } else if (byte === 0x3a || byte === 0x40) {
      this.connection.consume(1);
    } else if (byte === 0x25) {
      await this.parsePctEncoded();
    } else if (byte === 0x3f) {
      return;
    } else {
      throw new HTTPError(400, "Bad Request");
    }
  }

  async parseSegement() {
    while (true) {
      const byte = (await this.connection.read(1))[0];
      if (byte === 0x20 || byte === 0x2f) {
        return;
      }
      if (byte === 0x3f) {
        return;
      }
      await this.parsePchar();
    }
  }

  async parseQuery() {
    while (true) {
      const byte = (await this.connection.read(1))[0];
      if (byte === 0x20) {
        return;
      }
      if (byte === 0x3f || byte === 0x2f) {
        this.connection.consume(1);
      }
      await this.parsePchar();
    }
  }

  async parseAbsolutePath() {
    const byte = (await this.connection.read(1))[0];
    if (byte !== 0x2f) {
      throw new HTTPError(400, "Bad Request");
    }

    this.connection.consume(1);
    await this.parseSegement();
    while (true) {
      const byte = (await this.connection.read(1))[0];
      if (byte === 0x3f || byte === 0x20) {
        return;
      }
      if (byte !== 0x2f) {
        throw new HTTPError(400, "Bad Request");
      }
      this.connection.consume(1);
      await this.parseSegement();
    }
  }

  async parseURI() {
    await this.parseAbsolutePath();
    const byte = (await this.connection.read(1))[0];
    if (byte === 0x3f) {
      this.connection.consume(1);
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
      const byte = (await this.connection.read(1))[0];
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
      this.connection.consume(1);
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
      const byte = (await this.connection.read(1))[0];
      if (byte === 0x2f && current.isWord) {
        break;
      }
      if (!current.children.has(byte)) {
        throw new HTTPError(400, "Bad Request");
      }
      current = current.children.get(byte)!;
      this.connection.consume(1);
    }

    const slash = (await this.connection.read(1))[0];
    if (slash !== 0x2f) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);

    const lv = (await this.connection.read(1))[0];
    if (lv !== 0x31) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
    const dot = (await this.connection.read(1))[0];
    if (dot !== 0x2e) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);

    const rv = (await this.connection.read(1))[0];
    if (rv !== 0x31) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
    return "1.1";
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
    const sc = (await this.connection.read(1))[0];
    if (sc !== 0x3a) {
      throw new HTTPError(400, "Bad Request");
    }
    await this.parseOWS();
    await this.parseFieldValue();
    await this.parseOWS();
  }

  async parseToken() {
    await this.parseTchar();
    while (true) {
      const byte = (await this.connection.read(1))[0];
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
      const byte = (await this.connection.read(1))[0];
      if (!this.isFieldVchar(byte)) {
        return;
      }
      await this.parseFieldContent();
    }
  }

  async parseFieldContent() {
    await this.parseFieldVchar();
    const [fb, sb] = await this.connection.read(2);
    if (fb !== 0x20 && fb !== 0x09 && !this.isFieldVchar(fb)) {
      return;
    }
    if (sb !== 0x20 && sb !== 0x09 && !this.isFieldVchar(sb)) {
      await this.parseFieldVchar();
      return;
    }
    this.connection.consume(1);
    while (true) {
      const [fb, sb] = await this.connection.read(2);
      if (sb !== 0x20 && sb !== 0x09 && !this.isFieldVchar(sb)) {
        await this.parseFieldVchar();
        return;
      }
      this.connection.consume(1);
    }
  }

  async parseFieldVchar() {
    const byte = (await this.connection.read(1))[0];
    if (!this.isFieldVchar(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
  }

  async parseTchar() {
    const byte = (await this.connection.read(1))[0];
    if (!this.isTChar(byte)) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
  }

  async parseOWS() {
    while (true) {
      const byte = (await this.connection.read(1))[0];
      if (byte !== 0x20 && byte !== 0x09) {
        return;
      }
      this.connection.consume(1);
    }
  }

  async parseCRLF() {
    const fb = (await this.connection.read(1))[0];
    if (fb !== 0x0d) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
    const sb = (await this.connection.read(1))[0];
    if (sb !== 0x0a) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
  }

  async parseHeaders() {
    while (true) {
      const byte = (await this.connection.read(1))[0];
      if (!this.isTChar(byte)) {
        return;
      }
      await this.parseFieldLine();
      await this.parseCRLF();
    }
  }
}
