export class SecWebSocketKeyParser {
  value: string;
  index: number;
  constructor(value: string) {
    this.value = value;
    this.index = 0;
  }

  isDIGIT(b: number) {
    return b >= 0x30 && b <= 0x39;
  }

  isALPHA(b: number) {
    return (b >= 0x61 && b <= 0x7a) || (b >= 0x41 && b <= 0x5a);
  }

  isBase64Character(b: number) {
    return this.isALPHA(b) || this.isDIGIT(b) || b === 0x2b || b === 0x2f;
  }

  parseSebWebSocketKey() {
    try {
      this.parse64ValueNonEmpty();
      return true;
    } catch (err) {
      return false;
    }
  }

  parse64ValueNonEmpty() {
    const bytes = this.peekN(4);
    if (bytes[2] === 0x3d || bytes[3] === 0x3d) {
      this.parseBase64Padding();
    }
    if (this.isEOFReached()) {
      return;
    }
    this.parseBase64Data();
    while (!this.isEOFReached()) {
      const bytes = this.peekN(4);
      if (bytes[2] === 0x3d || bytes[3] === 0x3d) {
        this.parseBase64Padding();
      }
      if (this.isEOFReached()) {
        return;
      }
      this.parseBase64Data();
    }
  }

  parseBase64Data() {
    this.parse64Character();
    this.parse64Character();
    this.parse64Character();
    this.parse64Character();
  }

  parseBase64Padding() {
    this.parse64Character();
    this.parse64Character();
    const b1 = this.peek();
    if (this.isBase64Character(b1)) {
      this.parse64Character();
    } else if (b1 === 0x3d) {
      this.consume();
    } else {
      throw new Error("Invalid SecWebSocketKey");
    }
    const b2 = this.peek();
    if (b2 !== 0x3d) {
      throw new Error("Invalid SecWebSocketKey");
    }
    this.consume();
  }

  parse64Character() {
    const byte = this.peek();
    if (!this.isBase64Character(byte)) {
      throw new Error("Invalid SecWebSocketKey");
    }
    this.consume();
  }

  peek() {
    if (this.index >= this.value.length) {
      throw new Error("Invalid Peek");
    }
    return this.value[this.index].charCodeAt(0);
  }

  peekN(n: number) {
    if (n <= 0 || this.index + n - 1 >= this.value.length) {
      throw new Error("Invalid Peek");
    }
    return this.value
      .slice(this.index, this.index + n)
      .split("")
      .map((c) => c.charCodeAt(0));
  }

  consume() {
    if (this.index >= this.value.length) {
      throw new Error("Invalid Consume");
    }
    this.value[this.index++];
  }

  isEOFReached() {
    return this.index === this.value.length;
  }
}
