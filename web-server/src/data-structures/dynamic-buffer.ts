export class DynamicBuffer {
  data: Buffer;
  length: number;
  beg: number;
  constructor() {
    this.data = Buffer.from("");
    this.length = 0;
    this.beg = 0;
  }

  push(buffer: Buffer) {
    const newLength = this.length + buffer.length;
    if (this.data.length < newLength) {
      let capacity = Math.max(this.data.length, 32);
      while (capacity < newLength) {
        capacity *= 2;
      }
      const grown = Buffer.alloc(capacity);
      this.data.copy(grown, 0, 0);
      this.data = grown;
    }

    buffer.copy(this.data, this.length, 0);
    this.length = newLength;
  }
  consume(size: number = 1) {
    if (size > this.length - this.beg) {
      throw new Error("Not Enough Data To Consume");
    }
    this.beg += size;
  }

  unconsume() {
    if (this.beg <= 0) {
      throw new Error("No Data To Unconsume");
    }
    this.beg--;
  }

  skip() {
    this.data.copyWithin(0, this.beg, this.data.length);
    this.length = this.length - this.beg;
    this.beg = 0;
  }

  subarray(start: number = 0, end: number = this.length) {
    if (start < 0 || end >= this.data.length || start > end) {
      throw new Error("Invalid Subarray Operation");
    }
    return this.data.subarray(start, end);
  }

  readFromBeg(size: number) {
    if (this.beg + size >= this.data.length) {
      throw new Error("Invalid Read");
    }
    return this.subarray(this.beg, this.beg + size);
  }

  readAll() {
    return this.data.subarray(0, this.beg);
  }

  isReadable() {
    return this.beg < this.length;
  }
}
