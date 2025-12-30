import { createServer, Server, Socket } from "net";
import { HTTPConnection } from "./http-connection";
import { TCPConnection } from "../tcp-core/tcp-connection";
import { DynamicBuffer } from "../data-structures/dynamic-buffer";
import { HTTPError } from "./http-error";
import { HTTPRequestParser } from "./http-request-parser";
import { HTTPResponse } from "./http-response";

class HTTPServer {
  socket: Server;
  constructor(port: number, hostname: string) {
    this.socket = createServer({ pauseOnConnect: true });
    this.socket.on("connection", (socket: Socket) => this.init(socket));
    this.socket.listen(port, hostname);
    console.log(`Server Listening on ${hostname}:${port}`);
  }

  async init(socket: Socket) {
    console.log(`New Connection ${socket.remoteAddress}:${socket.remotePort}`);
    const connection = new HTTPConnection(new TCPConnection(socket), new DynamicBuffer());
    try {
      await this.serve(connection);
    } catch (err) {
      console.error(err);
    } finally {
      socket.destroy();
    }
  }

  async serve(connection: HTTPConnection) {
    try {
      while (true) {
        const httpRequest = await new HTTPRequestParser(connection).parseRequest();
        switch (httpRequest.uri) {
          case "/echo":
            if (httpRequest.method === "GET") {
              const httpResponse = new HTTPResponse(200, Buffer.from("Hello! To send data, please use the echo server: POST /echo"));
              await httpResponse.send(connection);
              break;
            }
            if (httpRequest.method === "POST") {
              const httpResponse = new HTTPResponse(200, httpRequest.body);
              await httpResponse.send(connection);
              break;
            }
          default:
            throw new HTTPError(404, "Not Found");
        }
      }
    } catch (err) {
      if (err instanceof HTTPError) {
        const httpResponse = new HTTPResponse(err.code, Buffer.from(err.message));
        await httpResponse.send(connection);
      }
      throw err;
    }
  }
}

export const createHTTPServer = (port: number, hostname: string) => {
  return new HTTPServer(port, hostname);
};
