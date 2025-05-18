class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.frequency = 0

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, frequency=1):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end_of_word = True
        node.frequency += frequency

    def search_prefix(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def collect_words(self, node, prefix, result):
        if node.is_end_of_word:
            result.append((node.frequency, prefix))
        for ch, child in node.children.items():
            self.collect_words(child, prefix + ch, result)

    def auto_suggest(self, prefix, limit=10):
        node = self.search_prefix(prefix)
        if not node:
            return []
        result = []
        self.collect_words(node, prefix, result)
        return [word for _, word in sorted(result, key=lambda x: -x[0])[:limit]]
