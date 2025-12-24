import { HTTPConnection } from "./http-connection";

export class HTTPResponse {
  code: number;
  body: Buffer;
  headers: string[][];
  constructor(code: number, body: Buffer, headers: string[][] = []) {
    this.code = code;
    this.body = body;
    this.headers = headers;
    if (this.body.length) {
      this.headers.push(["Content-Length", body.length.toString()]);
    }
  }
  generateResponseHeader() {
    const statusLine = `HTTP/1.1 ${this.code.toString()} ${REASON_PHRASE_BY_STATUS_CODE[this.code]} \r\n`;
    const headers = [`X-Powered-By: HTTP Echo Server\r\nContent-Type: charset=utf-8\r\n`];
    for (const header of this.headers) {
      headers.push(`${header[0]}: ${header[1]}\r\n`);
    }

    return Buffer.from(`${statusLine}${headers.join("")}\r\n`);
  }

  async send(connection: HTTPConnection) {
    const header = this.generateResponseHeader();
    await connection.write(header);
    await connection.write(this.body);
  }
}

const REASON_PHRASE_BY_STATUS_CODE: Record<number, string> = {
  200: "OK",
  201: "Created",
  400: "Bad Request",
  404: "Not Found",
  413: "Payload Too Large",
  431: "Request Header Fields Too Large",
  500: "Internal Server Error",
};
