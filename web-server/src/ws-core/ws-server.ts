import { BlockingQueue } from "../data-structures/blocking-queue";
import { HTTPConnection } from "../http-core/http-connection";
import { WSFrame } from "./ws-frame";
import { WSMessageParser } from "./ws-frame-parser";
import { WSMessage } from "./ws-message";

export class WSServer {
  connection: HTTPConnection;
  // Blocking Queues for multi producer/consumer tasks
  sendQeue: BlockingQueue<WSFrame>;
  rcvQueue: BlockingQueue<WSMessage>;
  constructor(connection: HTTPConnection) {
    this.connection = connection;
    this.sendQeue = new BlockingQueue<WSFrame>();
    this.rcvQueue = new BlockingQueue<WSMessage>();
  }
  async rcvServer() {
    while (true) {
      const wsMessage = await new WSMessageParser(this.connection).parse();
      this.rcvQueue.produce(wsMessage);
      const msg = await this.rcv();
      if (msg) {
        this.send(new WSFrame(1, 1, 0, 0, msg.payload));
      }
    }
  }

  async sendServer() {
    while (true) {
      const wsFrame = await this.sendQeue.consume();
      if (wsFrame) {
        await this.connection.write(wsFrame.generate());
      }
    }
  }

  async send(wsFrame: WSFrame) {
    await this.sendQeue.produce(wsFrame);
  }

  async rcv() {
    return await this.rcvQueue.consume();
  }

  async serve() {
    try {
      await Promise.all([this.rcvServer(), this.sendServer()]);
    } catch (err) {
      this.close();
      throw err;
    }
  }

  close() {
    this.sendQeue.close();
    this.rcvQueue.close();
  }
}
