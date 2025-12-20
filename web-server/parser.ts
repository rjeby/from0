class Parser {
  uri: string;
  index: number;

  constructor(uri: string) {
    this.uri = uri;
    this.index = 0;
  }

  peek() {
    if (this.index >= this.uri.length) {
      throw new Error("Invalid URI");
    }
    return this.uri[this.index];
  }

  consume() {
    if (this.index >= this.uri.length) {
      throw new Error("Invalid URI");
    }
    this.index++;
  }

  hasNext() {
    return this.index < this.uri.length;
  }

  isHEXDIG(c: string): boolean {
    return (c >= "0" && c <= "9") || (c >= "A" && c <= "F");
  }

  isDIGIT(c: string) {
    return c >= "0" && c <= "9";
  }

  isALPHA(c: string) {
    return (c >= "a" && c <= "z") || (c >= "A" && c <= "Z");
  }

  isUnreserved(c: string) {
    return this.isALPHA(c) || this.isDIGIT(c) || c === "-" || c === "." || c === "_" || c === "~";
  }

  isSubDelims(c: string): boolean {
    return c === "!" || c === "$" || c === "&" || c === "'" || c === "(" || c === ")" || c === "*" || c === "+" || c === "," || c === ";" || c === "=";
  }

  parseUnreserved() {
    const c = this.peek();
    if (!this.isUnreserved(c)) {
      throw new Error("Invalid URI");
    }
    this.consume();
    return c;
  }

  parsePctEncoded() {
    const c = this.peek();
    if (c !== "%") {
      throw new Error("Invalid URI");
    }
    this.consume();
    const hx1 = this.parseHEXDIG();
    const hx2 = this.parseHEXDIG();
    return [c, hx1, hx2].join();
  }

  parseHEXDIG() {
    const c = this.peek();
    if (!this.isHEXDIG(c)) {
      throw new Error("Invalid URI");
    }
    this.consume();
    return c;
  }

  parseSubDelims() {
    const c = this.peek();
    if (!this.isSubDelims(c)) {
      throw new Error("Invalid URI");
    }
    this.consume();
    return c;
  }

  parsePchar() {
    const c = this.peek();
    if (this.isUnreserved(c)) {
      return this.parseUnreserved();
    } else if (this.isSubDelims(c)) {
      return this.parseSubDelims();
    } else if (c === ":" || c === "@") {
      this.consume();
      return c;
    } else if (c === "%") {
      return this.parsePctEncoded();
    } else {
      throw new Error("Invalid URI");
    }
  }

  parseSegement() {
    const segment = [];
    while (this.hasNext()) {
      const c = this.peek();
      if (c === "/") {
        return segment.join("");
      }
      const pchar = this.parsePchar();
      segment.push(pchar);
    }

    return segment.join("");
  }

  parseAbsolutePath() {
    const absolutePath = [];
    do {
      const c = this.peek();
      if (c !== "/") {
        throw new Error("Invalid URI");
      }
      this.consume();
      const segment = this.parseSegement();
      absolutePath.push(["/", segment].join(""));
    } while (this.hasNext());

    return absolutePath.join("");
  }

  parseURI() {
    return this.parseAbsolutePath();
  }
}

