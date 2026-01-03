export class WSMessage {
  type: number;
  payload: Buffer;
  constructor(type: number, payload: Buffer) {
    this.type = type;
    this.payload = payload;
  }
}
