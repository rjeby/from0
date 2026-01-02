import { HTTPConnection } from "../http-core/http-connection";
import { WSError } from "./ws-error";
import { WSMessage } from "./ws-message";

const MAX_MESSAGE_SIZE = 10 * 1024 * 1024;

export class WSMessageParser {
  connection: HTTPConnection;
  messageSize: number;
  constructor(connection: HTTPConnection) {
    this.messageSize = 0;
    this.connection = connection;
  }

  consume() {
    this.connection.consume();
  }

  addFragmentSize(fragementSize: number) {
    if (this.messageSize + fragementSize > MAX_MESSAGE_SIZE) {
      throw new WSError("Max Message Size Limit Exceeded");
    }
    this.messageSize += fragementSize;
  }

  async parse() {
    const [fin, opcode, maskingKey, payload] = await this.parseFrame();
    this.connection.skip();
    return new WSMessage(opcode, payload);
  }

  async parseFrame(): Promise<[number, number, number, Buffer]> {
    const [fin, opcode] = await this.parseMSByte();
    // console.log("| FIN: ", fin, "| OPCODE: ", opcode);
    const [mask, length] = await this.parsePayloadLength();
    // console.log("| MASK: ", fin, "| LENGTH: ", opcode);
    const maskingKey = await this.parseMaskingKey(mask);
    // console.log("| MASKING KEY: ", maskingKey);
    const payload = await this.parsePayload(length, maskingKey);
    // console.log("| PAYLOAD: ", payload);
    return [fin, opcode, maskingKey, payload];
  }

  async parsePayload(length: number, mask: number) {
    const maskBytes = [mask >> 24, (mask >> 16) & 0b11111111, (mask >> 8) & 0b11111111, mask & 0b11111111];
    const payload = Buffer.from(await this.connection.readBytes(length));
    let index = 0;
    this.connection.consume(length);
    for (let byte = 0; byte < payload.length; byte++) {
      payload[byte] = payload[byte] ^ maskBytes[index % 4];
      index++;
    }
    return payload;
  }

  async parseMaskingKey(mask: number) {
    if (!mask) {
      return 0;
    }
    let key = 0;
    for (let index = 0; index < 4; index++) {
      const byte = await this.connection.readByte();
      key = (key << 8) + byte;
      this.consume();
    }
    return key;
  }

  async parseMSByte() {
    const byte = await this.connection.readByte();
    const fin = byte >> 7;
    const rsv = (byte >> 4) & 0b111;
    if (rsv) {
      throw new WSError("Invalid RSV");
    }
    const opcode = byte & 0b1111;
    this.consume();
    return [fin, opcode];
  }

  async parsePayloadLength() {
    const byte = await this.connection.readByte();
    const mask = byte >> 7;
    const length = byte & 0b1111111;
    this.consume();
    if (length < 126) {
      const payloadLength = length;
      this.addFragmentSize(payloadLength);
      return [mask, payloadLength];
    }
    if (length === 126) {
      const payloadLength = await this.parse16BitsPayloadLength();
      this.addFragmentSize(payloadLength);
      return [mask, payloadLength];
    }
    const payloadLength = await this.parse64BitsPayloadLength();
    this.addFragmentSize(payloadLength);
    return [mask, payloadLength];
  }

  async parse16BitsPayloadLength() {
    let length = 0;
    for (let index = 0; index < 2; index++) {
      const byte = await this.connection.readByte();
      length = (length << 8) + byte;
      this.consume();
    }
    return length;
  }

  async parse64BitsPayloadLength() {
    let length = 0;
    const msbByte = await this.connection.readByte();
    if (msbByte >> 7) {
      throw new WSError("Invalid Payload Length");
    }
    this.connection.consume();
    for (let index = 0; index < 3; index++) {
      const byte = await this.connection.readByte();
      length = (length << 8) + byte;
      this.consume();
    }
    return length;
  }
}
