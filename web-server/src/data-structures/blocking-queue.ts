class ListNode<T> {
  value: T;
  next: ListNode<T> | null;
  constructor(value: T, next: ListNode<T> | null) {
    this.value = value;
    this.next = next;
  }
}

class Queue<T> {
  head: ListNode<T> | null;
  tail: ListNode<T> | null;
  constructor() {
    this.head = null;
    this.tail = null;
  }

  pushBack(value: T) {
    if (!this.tail) {
      this.head = new ListNode(value, null);
      this.tail = this.head;
      return;
    }
    this.tail.next = new ListNode(value, null);
    this.tail = this.tail.next;
  }

  popFront() {
    if (!this.head) {
      throw new Error("Empty Queue");
    }
    const value = this.head.value;
    if (this.head === this.tail) {
      this.head = null;
      this.tail = null;
      return value;
    }
    this.head = this.head.next;
    return value;
  }

  isEmpty() {
    return !this.head;
  }

  toString() {
    const elements = [];
    let current = this.head;
    while (current) {
      elements.push(current.value);
      current = current.next;
    }
    elements.push("END");
    return elements.join(" --> ");
  }
}
class Producer<T> {
  resolve: () => void;
  reject: (reason: string) => void;
  value: T;
  constructor(value: T, resolve: () => void, reject: (reason: string) => void) {
    this.resolve = resolve;
    this.reject = reject;
    this.value = value;
  }
  fulfill() {
    this.resolve();
  }
  abort(reason: string) {
    this.reject(reason);
  }
}

class Consumer<T> {
  resolve: (value: T | null) => void;
  constructor(resolve: (value: T | null) => void) {
    this.resolve = resolve;
  }
  fulfill(value: T | null) {
    this.resolve(value);
  }
}

export class BlockingQueue<T> {
  producers: Queue<Producer<T>>;
  consumers: Queue<Consumer<T>>;
  isClosed: boolean;
  constructor() {
    this.producers = new Queue<Producer<T>>();
    this.consumers = new Queue<Consumer<T>>();
    this.isClosed = false;
  }

  produce(value: T): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isClosed) {
        return reject("Closed Queue");
      }
      if (!this.consumers.isEmpty()) {
        const consumer = this.consumers.popFront();
        consumer.fulfill(value);
        return resolve();
      }
      const producer = new Producer<T>(value, resolve, reject);
      this.producers.pushBack(producer);
    });
  }

  consume() : Promise<T | null> {
    return new Promise((resolve) => {
      if (this.isClosed) {
        resolve(null);
      }
      if (!this.producers.isEmpty()) {
        const producer = this.producers.popFront();
        producer.fulfill();
        return resolve(producer.value);
      }
      const consumer = new Consumer(resolve);
      this.consumers.pushBack(consumer);
    });
  }

  close() {
    this.isClosed = true;
    while (!this.producers.isEmpty) {
      const producer = this.producers.popFront();
      producer.abort("Closed Queue");
    }
    while (!this.consumers.isEmpty) {
      const consumer = this.consumers.popFront();
      consumer.fulfill(null);
    }
  }
}
