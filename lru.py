#!/usr/bin/env python3
from typing import Any, Optional
 
class Node:
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
 
class LRUCache:
    """
    Least Recently Used (LRU) Cache implementation.
    Provides O(1) operations for get, has, and set.
    """
 
    def __init__(self, item_limit: int):
        self.capacity = item_limit
        self.cache = {}
        self.head = Node(None, None)  # dummy head
        self.tail = Node(None, None)  # dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head
 
    def _remove(self, node: Node):
        prev_node, next_node = node.prev, node.next
        prev_node.next = next_node
        next_node.prev = prev_node
 
    def _add_to_front(self, node: Node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
 
    def has(self, key: str) -> bool:
        """Check if key is in cache. Updates LRU order if found."""
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add_to_front(node)
            return True
        return False
 
    def get(self, key: str) -> Optional[Any]:
        """Get value for key if present. Updates LRU order if found."""
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add_to_front(node)
            return node.value
        return None
 
    def set(self, key: str, value: Any):
        """Insert or update value for key. Evicts LRU if over capacity."""
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)