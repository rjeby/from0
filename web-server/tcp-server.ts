import { createServer, Socket } from "net";

class TCPConnection {
  socket: Socket;
  reader: null | {
    resolve: (data: Buffer) => void;
    reject: (reason: Error) => void;
  };
  ended: boolean;
  error: null | Error;

  constructor(socket: Socket) {
    this.socket = socket;
    this.reader = null;
    this.ended = false;
    this.error = null;

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
  while (true) {
    const data = await connection.read();
    console.log("DATA: ", data.toString())
    if (!data.length) {
      break;
    }
    await connection.write(data);
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
