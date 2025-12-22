import { createServer, Socket } from "net";
import { HTTPRequestParser } from "./parser";

export class HTTPConnection {
  connection: TCPConnection;
  buffer: DynamicBuffer;
  constructor(connection: TCPConnection, buffer: DynamicBuffer) {
    this.connection = connection;
    this.buffer = buffer;
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

      resolve(this.buffer.subarray(1)[0]);
    });
  }

  consume() {
    this.buffer.consume();
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

  consume() {
    // this.data.copyWithin(0, size, this.data.length);
    // this.length = this.length - size;
    if (this.beg >= this.length) {
      throw new Error("Invalid Consume Operation");
    }
    this.beg++;
  }

  unconsume() {
    if (this.beg <= 0) {
      throw new Error("Invalid Unconsume Operation");
    }
    this.beg--;
  }

  subarray(end: number) {
    if (end < 0) {
      throw new Error("Invalid Subarray Operation");
    }
    return this.data.subarray(this.beg, this.beg + end);
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

const serveClient = async (socket: Socket) => {
  const connection = new HTTPConnection(new TCPConnection(socket), new DynamicBuffer());

  while (true) {
    await new HTTPRequestParser(connection).parseRequest();
    socket.destroy();
    break;
  }
};

const initConnection = async (socket: Socket) => {
  console.log(`New Connection ${socket.remoteAddress}:${socket.remotePort}`);
  try {
    await serveClient(socket);
  } catch (err) {
    console.error(err);
  } finally {
    socket.destroy();
  }
};

const server = createServer({ pauseOnConnect: true });
server.on("connection", (socket) => initConnection(socket));
server.listen(1234, "localhost");
