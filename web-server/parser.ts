import { HTTPConnection, HTTPError } from "./tcp-server";
import { HTTP_TRIE, METHOD_TRIE } from "./trie";

export class HTTPRequestParser {
  connection: HTTPConnection;
  constructor(connection: HTTPConnection) {
    this.connection = connection;
  }

  async parseRequest() {
    const method = await new HTTPMethodParser(this.connection).parseMethod();
    const uri = await new HTTPUriParser(this.connection).parseURI();
    const version = await new HTTPVersionParser(this.connection).parseVersion();
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
    return c;
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
      await this.parsePchar();
    }
  }

  async parseAbsolutePath() {
    const byte = (await this.connection.read(1))[0];
    if (byte !== 0x2f) {
      throw new HTTPError(400, "Bad Request");
    }

    this.connection.consume(1);
    while (true) {
      const byte = (await this.connection.read(1))[0];
      if (byte === 0x20) {
        this.connection.consume(1);
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
    return await this.parseAbsolutePath();
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
      const c = await this.connection.read(1);
      const uc = c.toString();
      if (c.equals(Buffer.from(" ")) && !current.isWord) {
        throw new HTTPError(400, "Bad Request");
      }
      if (c.equals(Buffer.from(" "))) {
        this.connection.consume(1);
        return method.join("");
      }
      if (!current.children.has(uc)) {
        throw new HTTPError(400, "Bad Request");
      }
      method.push(uc);
      current = current.children.get(uc)!;
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
      const c = await this.connection.read(1);
      const uc = c.toString();
      if (c.equals(Buffer.from("/")) && current.isWord) {
        this.connection.consume(1);
        break;
      }
      if (!current.children.has(uc)) {
        throw new HTTPError(400, "Bad Request");
      }
      current = current.children.get(uc)!;
      this.connection.consume(1);
    }

    const lv = await this.connection.read(1);
    if (!lv.equals(Buffer.from("1"))) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
    const dot = await this.connection.read(1);
    if (!dot.equals(Buffer.from("."))) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);

    const rv = await this.connection.read(1);
    if (!rv.equals(Buffer.from("1"))) {
      throw new HTTPError(400, "Bad Request");
    }
    this.connection.consume(1);
    return "1.1";
  }
}
