import { TCPConnection } from "../tcp-core/tcp-connection";
import { DynamicBuffer } from "../data-structures/dynamic-buffer";
import { HTTPError } from "./http-error";

export class HTTPConnection {
  connection: TCPConnection;
  buffer: DynamicBuffer;
  constructor(connection: TCPConnection, buffer: DynamicBuffer) {
    this.connection = connection;
    this.buffer = buffer;
  }

  skip() {
    this.buffer.skip();
  }

  close() {
    this.connection.socket.destroy();
  }

  async readByte(): Promise<number> {
    while (!this.buffer.isReadable()) {
      const data = await this.connection.read();
      if (!data.length) {
        throw new HTTPError(400, "Bad Request");
      }
      this.buffer.push(data);
    }
    const byte = this.buffer.readFromBeg(1)[0];
    return byte;
  }

  async readBytes(size: number): Promise<Buffer> {
    while (this.buffer.length - this.buffer.beg < size) {
      const data = await this.connection.read();
      if (!data.length) {
        throw new HTTPError(400, "Bad Request");
      }
      this.buffer.push(data);
    }
    const bytes = this.buffer.readFromBeg(size);
    return bytes;
  }

  async readAllConnection(): Promise<Buffer> {
    while (true) {
      const data = await this.connection.read();
      if (!data.length) {
        return Buffer.from(this.buffer.readAll());
      }
      this.buffer.push(data);
    }
  }

  async write(data: Buffer): Promise<void> {
    await this.connection.write(data);
  }

  consume(size: number = 1) {
    this.buffer.consume(size);
  }

  unconsume() {
    this.buffer.unconsume();
  }
}
