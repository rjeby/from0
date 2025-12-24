export class HTTPRequest {
  method: string;
  uri: string;
  version: string;
  header: Map<string, string>;
  body: Buffer;

  constructor(method: string, uri: string, version: string, header: Map<string, string>, body: Buffer) {
    this.method = method;
    this.uri = uri;
    this.version = version;
    this.header = header;
    this.body = body;
  }
}
