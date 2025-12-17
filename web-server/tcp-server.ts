import { createServer, Socket } from "net";

class DynamicBuffer {
  data: Buffer;
  length: number;
  constructor() {
    this.data = Buffer.from("");
    this.length = 0;
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

  consume(size: number) {
    this.data = this.data.subarray(size);
    this.length = this.length - size;
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
  const connection = new TCPConnection(socket);
  const buffer = new DynamicBuffer();
  while (true) {
    const message = readMessage(buffer);
    console.log("Message: ", message?.toString())
    if (message && message.equals(Buffer.from("quit\n"))) {
      await connection.write(Buffer.from("Bye.\n"));
      socket.destroy();
      return;
    }
    if (message) {
      const reply = Buffer.concat([Buffer.from("Echo: "), message]);
      await connection.write(reply);
      continue;
    }
    const data = await connection.read();
    buffer.push(data);
    if (!data.length) {
      break;
    }
  }
};

const readMessage = (buffer: DynamicBuffer) => {
  const index = buffer.data.subarray(0, buffer.length).indexOf("\n");
  if (index < 0) {
    return null;
  }
  const message = Buffer.from(buffer.data.subarray(0, index + 1));
  buffer.consume(index + 1);
  return message;
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
