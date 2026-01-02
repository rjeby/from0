import { HTTPConnection } from "../http-core/http-connection";
import { WSMessageParser } from "./ws-frame-parser";

export class WSServer {
  connection: HTTPConnection;
  constructor(connection: HTTPConnection) {
    this.connection = connection;
  }
  async rcvServer() {
    while (true) {
      const wsMessage = await new WSMessageParser(this.connection).parse();
      
    }
  }

  async sendServer() {}

  async serve() {
    await Promise.all([this.rcvServer(), this.sendServer()]);
  }
}
