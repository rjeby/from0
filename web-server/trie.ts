class TrieNode {
  children: Map<number, TrieNode>;
  isWord: boolean;
  constructor() {
    this.children = new Map();
    this.isWord = false;
  }
}

class Trie {
  root: TrieNode;
  constructor() {
    this.root = new TrieNode();
  }

  insert(word: string) {
    let current = this.root;
    for (const c of word) {
      let charCode = c.charCodeAt(0);
      if (!current.children.has(charCode)) {
        current.children.set(charCode, new TrieNode());
      }
      current = current.children.get(charCode)!;
    }
    current.isWord = true;
  }
}

const methodTrie = () => {
  const trie = new Trie();
  const methods = ["GET", "POST"];
  for (const method of methods) {
    trie.insert(method);
  }

  return trie;
};

const httpTrie = () => {
  const trie = new Trie();
  trie.insert("HTTP");
  return trie;
};

export const METHOD_TRIE: Trie = methodTrie();
export const HTTP_TRIE: Trie = httpTrie();
