import { HTTPConnection } from "../http-core/http-connection";
import { WSMessageParser } from "./ws-frame-parser";

export class WSServer {
  connection: HTTPConnection;
  constructor(connection: HTTPConnection) {
    this.connection = connection;
  }
  async rcvServer() {
    while (true) {
      console.log("Parsing Message");
      const wsMessage = await new WSMessageParser(this.connection).parse();
      console.log("| START");
      wsMessage.toString();
      console.log("| END");
    }
  }

  async sendServer() {}

  async serve() {
    await Promise.all([this.rcvServer(), this.sendServer()]);
  }
}
