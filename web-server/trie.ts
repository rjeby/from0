class TrieNode {
  children: Map<string, TrieNode>;
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
      if (!current.children.has(c)) {
        current.children.set(c, new TrieNode());
      }
      current = current.children.get(c)!;
    }
    current.isWord = true;
  }
}

const methodTrie = () => {
  const trie = new Trie();
  const methods = ["GET", "POST", "PUT", "DELETE"];
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
