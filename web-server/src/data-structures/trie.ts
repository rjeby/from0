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

const initTrie = (words: string[]) => {
  const trie = new Trie();
  for (const word of words) {
    trie.insert(word);
  }
  return trie;
};

export const METHOD_TRIE: Trie = initTrie(["GET", "POST"]);
export const HTTP_TRIE: Trie = initTrie(["HTTP"]);
