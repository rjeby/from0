import { createServer, Socket } from "net";
import { HTTPEchoResponse, HTTPRequestParser, HTTPResponse } from "./parser";

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

  readByte(): Promise<number> {
    return new Promise(async (resolve, reject) => {
      while (!this.buffer.isReadable()) {
        const data = await this.connection.read();
        if (!data.length) {
          reject(new HTTPError(400, "Bad Request"));
          return;
        }
        this.buffer.push(data);
      }

      resolve(this.buffer.readFromBeg(1)[0]);
    });
  }

  readBytes(size: number): Promise<Buffer> {
    return new Promise(async (resolve, reject) => {
      while (this.buffer.length - this.buffer.beg < size) {
        const data = await this.connection.read();
        if (!data.length) {
          reject(new HTTPError(400, "Bad Request"));
          return;
        }
        this.buffer.push(data);
      }

      resolve(this.buffer.subarray(this.buffer.beg, this.buffer.beg + size));
    });
  }

  readAllConnection(): Promise<Buffer> {
    return new Promise(async (resolve, reject) => {
      while (true) {
        const data = await this.connection.read();
        if (!data.length) {
          return Buffer.from(this.buffer.subarray(0, this.buffer.length));
        }
        this.buffer.push(data);
      }
    });
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

export class HTTPError extends Error {
  code: number;
  constructor(code: number, message: string) {
    super(message);
    this.code = code;
  }
}

class DynamicBuffer {
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
    if (this.beg + size - 1 >= this.length) {
      throw new Error("Invalid Consume Operation");
    }
    this.beg += size;
  }

  skip() {
    this.data.copyWithin(0, this.beg, this.data.length);
    this.length = this.length - this.beg;
    this.beg = 0;
  }

  unconsume() {
    if (this.beg <= 0) {
      throw new Error("Invalid Unconsume Operation");
    }
    this.beg--;
  }

  subarray(start: number, end: number) {
    if (start > end) {
      throw new Error("Invalid Subarray Operation");
    }
    return this.data.subarray(start, end);
  }

  readFromBeg(size: number) {
    return this.subarray(this.beg, this.beg + size);
  }

  isReadable() {
    return this.beg < this.length;
  }
}

class TCPConnection {
  socket: Socket;
  reader: null | {
    resolve: (data: Buffer) => void;
    reject: (reason: Error) => void;
  };
  ended: boolean;
  error: null | Error;
  queue: Array<String>;

  constructor(socket: Socket) {
    this.socket = socket;
    this.reader = null;
    this.ended = false;
    this.error = null;
    this.queue = [];

    socket
      .on("data", (data: Buffer) => {
        console.assert(this.reader !== null);
        this.socket.pause();
        this.reader!.resolve(data);
        this.reader = null;
      })
      .on("end", () => {
        this.ended = true;
        if (this.reader) {
          this.reader.resolve(Buffer.from(""));
          this.reader = null;
        }
      })
      .on("error", (error: Error) => {
        this.error = error;
        if (this.reader) {
          this.reader.reject(error);
          this.reader = null;
        }
      });
  }

  read(): Promise<Buffer> {
    console.assert(this.reader === null);
    return new Promise((resolve, reject) => {
      if (this.error) {
        reject(this.error);
        return;
      }

      if (this.ended) {
        resolve(Buffer.from(""));
        return;
      }

      this.reader = { resolve: resolve, reject: reject };
      this.socket.resume();
    });
  }

  write(data: Buffer): Promise<void> {
    console.assert(data.length > 0);
    return new Promise((resolve, reject) => {
      if (this.error) {
        reject(this.error);
      }
      this.socket.write(data, (err) => {
        if (err) {
          reject(err);
          return;
        }
        resolve();
      });
    });
  }
}

const serveClient = async (connection: HTTPConnection) => {
  while (true) {
    const httpRequest = await new HTTPRequestParser(connection).parseRequest();
    const method = httpRequest.method;
    const uri = httpRequest.uri;
    const contentLength = Number(httpRequest.getField("content-length"));
    const transferEncoding = httpRequest.getField("transfer-encoding");
    if (uri !== "/echo") {
      throw new HTTPError(404, "Not Found");
    }

    if (method === "GET") {
      const response = new HTTPResponse(200, Buffer.from("Hello! To send data, please use the echo server: POST /echo\n"));
      await new HTTPEchoResponse(connection, response).sendMessage();
      continue;
    }

    if (contentLength > 0) {
      const body = await connection.readBytes(contentLength);
      const response = new HTTPResponse(200, body);
      await new HTTPEchoResponse(connection, response).sendMessage();
      connection.consume(contentLength);
      connection.skip();
    } else if (transferEncoding === "chunked") {
      const response = new HTTPResponse(200, Buffer.from(""), [["Transfer-Encoding", "chunked"]]);
      await new HTTPEchoResponse(connection, response).sendChunked();
      connection.skip();
    } else {
      const body = await connection.readAllConnection();
      const response = new HTTPResponse(200, body);
      await new HTTPEchoResponse(connection, response).sendMessage();
      break;
    }
  }
};

const initConnection = async (socket: Socket) => {
  console.log(`New Connection ${socket.remoteAddress}:${socket.remotePort}`);
  const connection = new HTTPConnection(new TCPConnection(socket), new DynamicBuffer());
  try {
    await serveClient(connection);
  } catch (err) {
    console.error(err);
    if (err instanceof HTTPError) {
      const response = new HTTPResponse(err.code, Buffer.from(err.message));
      try {
        await new HTTPEchoResponse(connection, response).sendMessage();
      } catch (err) {}
    }
  } finally {
    socket.destroy();
  }
};

const server = createServer({ pauseOnConnect: true });
server.on("connection", (socket) => initConnection(socket));
server.listen(1234, "localhost");
