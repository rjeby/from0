import { WSError } from "./ws-error";

const MAX_MESSAGE_SIZE = 10 * 1024 * 1024;

export class WSFrame {
  fin: number;
  opcode: number;
  masked: number;
  maskingKey: number;
  payload: Buffer;
  constructor(fin: number, opcode: number, masked: number, maskingKey: number, payload: Buffer) {
    if (payload.length > MAX_MESSAGE_SIZE) {
      throw new WSError("Max Message Size Limit Exceeded");
    }
    this.fin = fin;
    this.opcode = opcode;
    this.masked = masked;
    this.maskingKey = maskingKey;
    this.payload = payload;
  }

  generate() {
    const header = [];
    const payloadLengthInBits = this.payloadLengthInBits();
    const fb = ((this.fin & 0b1) << 7) + ((this.opcode) & 0b1111);
    header.push(fb);
    const sb = ((this.masked & 0b1) << 7) + (payloadLengthInBits === 7 ? this.payload.length : 0b1111111);
    header.push(sb);
    if (payloadLengthInBits !== 7) {
      header.push(this.payload.length);
    }
    return Buffer.concat([Buffer.from(header), this.payload]);
  }

  toString() {
    const frame = this.generate();
    const res = [];
    let byteIndex = 0;
    for (const byte of frame) {
      res.push(`|${this.toBinary(byte)}|`);
      res.push("  ");
      byteIndex++;
      if (byteIndex === 4) {
        res.push("\n");
        byteIndex = 0;
      }
    }

    return res.join("");
  }

  toBinary(byte: number) {
    const binary = [];
    for (let i = 7; i >= 0; i--) {
      binary.push((byte >> i) & 0b1);
    }
    return binary.join("");
  }

  payloadLengthInBits() {
    const payloadLength = this.payload.length;
    if (payloadLength <= 125) {
      return 7;
    } else if (payloadLength <= (1 << 16) - 1) {
      return 16;
    } else {
      return 64;
    }
  }
}
