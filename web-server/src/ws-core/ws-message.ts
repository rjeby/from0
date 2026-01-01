export class WSMessage {
  type: number;
  payload: Buffer;
  constructor(type: number, payload: Buffer) {
    this.type = type;
    this.payload = payload;
  }

  toString() {
    const LINE_LENGTH = 100;
    const length = this.payload.length;
    console.log("| Type: ");
    console.log("|", this.type);
    for (let beg = 0; beg < length; beg += LINE_LENGTH) {
      const end = Math.max(beg + LINE_LENGTH, length);
      console.log("|", this.payload.subarray(beg, end).toString("ascii"));
    }
  }
}
