"""
DataStructures.py - Custom data structure implementations
NO built-in dictionaries or maps - all custom implementations!

This file contains:
1. Array - Fixed-size array
2. LinkedList - Singly linked list
3. Stack - LIFO stack using array
4. Queue - FIFO queue using circular array
5. HashTable - Hash table with chaining (replaces dict)
6. AdjacencyList - Graph adjacency list for zones
"""


# ============================================
# 1. ARRAY CLASS - Fixed-size array
# ============================================
class Array:
    """
    Fixed-size array implementation
    Used for: Parking slots in each area
    """
    
    def __init__(self, capacity=100):
        """Initialize array with fixed capacity"""
        self.capacity = capacity
        self.items = [None] * capacity
        self.size = 0
    
    def append(self, item):
        """Add item to end - O(1)"""
        if self.size >= self.capacity:
            raise Exception(f"Array is full (capacity: {self.capacity})")
        self.items[self.size] = item
        self.size += 1
        return True
    
    def get(self, index):
        """Get item at index - O(1)"""
        if 0 <= index < self.size:
            return self.items[index]
        raise IndexError(f"Index {index} out of range (size: {self.size})")
    
    def set(self, index, value):
        """Set item at index - O(1)"""
        if 0 <= index < self.size:
            self.items[index] = value
            return True
        raise IndexError(f"Index {index} out of range (size: {self.size})")
    
    def remove(self, item):
        """Remove first occurrence - O(n)"""
        for i in range(self.size):
            if self.items[i] == item:
                # Shift all elements left
                for j in range(i, self.size - 1):
                    self.items[j] = self.items[j + 1]
                self.items[self.size - 1] = None
                self.size -= 1
                return True
        return False
    
    def find(self, item):
        """Find index of item - O(n)"""
        for i in range(self.size):
            if self.items[i] == item:
                return i
        return -1
    
    def get_all(self):
        """Return list of all items"""
        return [self.items[i] for i in range(self.size)]
    
    def clear(self):
        """Clear all items"""
        for i in range(self.size):
            self.items[i] = None
        self.size = 0
    
    def __len__(self):
        return self.size
    
    def __iter__(self):
        """Make array iterable"""
        for i in range(self.size):
            yield self.items[i]
    
    def __str__(self):
        return f"Array(size={self.size}, capacity={self.capacity})"


# ============================================
# 2. NODE CLASS - For linked structures
# ============================================
class Node:
    """Node for linked list"""
    def __init__(self, data):
        self.data = data
        self.next = None


# ============================================
# 3. LINKED LIST CLASS - Singly linked list
# ============================================
class LinkedList:
    """
    Singly linked list implementation
    Used for: Parking areas in each zone
    """
    
    def __init__(self):
        self.head = None
        self.size = 0
    
    def append(self, data):
        """Add item to end - O(n)"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1
        return True
    
    def prepend(self, data):
        """Add item to beginning - O(1)"""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1
        return True
    
    def delete(self, data):
        """Delete first occurrence - O(n)"""
        if not self.head:
            return False
        
        # If head contains data
        if self.head.data == data:
            self.head = self.head.next
            self.size -= 1
            return True
        
        # Search in rest of list
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        return False
    
    def search(self, data):
        """Search for data - O(n)"""
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False
    
    def get_all(self):
        """Return list of all data - O(n)"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def clear(self):
        """Clear all nodes"""
        self.head = None
        self.size = 0
    
    def __len__(self):
        return self.size
    
    def __iter__(self):
        """Make linked list iterable"""
        current = self.head
        while current:
            yield current.data
            current = current.next
    
    def __str__(self):
        return f"LinkedList(size={self.size})"


# ============================================
# 4. STACK CLASS - LIFO using array
# ============================================
class Stack:
    """
    Stack implementation using array (LIFO - Last In First Out)
    Used for: Rollback operations history
    """
    
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.items = [None] * capacity
        self.top = -1
    
    def push(self, item):
        """Push item onto stack - O(1)"""
        if self.top >= self.capacity - 1:
            raise Exception(f"Stack overflow (capacity: {self.capacity})")
        self.top += 1
        self.items[self.top] = item
        return True
    
    def pop(self):
        """Pop item from stack - O(1)"""
        if self.top < 0:
            return None
        item = self.items[self.top]
        self.items[self.top] = None
        self.top -= 1
        return item
    
    def peek(self):
        """View top item without removing - O(1)"""
        if self.top < 0:
            return None
        return self.items[self.top]
    
    def is_empty(self):
        """Check if stack is empty - O(1)"""
        return self.top < 0
    
    def size(self):
        """Get number of items - O(1)"""
        return self.top + 1
    
    def get_recent(self, n):
        """Get n most recent items (for history display) - O(n)"""
        if n <= 0 or self.top < 0:
            return []
        count = min(n, self.top + 1)
        result = []
        for i in range(count):
            result.append(self.items[self.top - i])
        return result
    
    def clear(self):
        """Clear all items - O(n)"""
        for i in range(self.top + 1):
            self.items[i] = None
        self.top = -1
    
    def __len__(self):
        return self.top + 1
    
    def __str__(self):
        return f"Stack(size={self.size()}, capacity={self.capacity})"


# ============================================
# 5. QUEUE CLASS - FIFO using circular array
# ============================================
class Queue:
    """
    Queue implementation using circular array (FIFO - First In First Out)
    Used for: Pending parking requests
    """
    
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.items = [None] * capacity
        self.front = 0
        self.rear = -1
        self.count = 0
    
    def enqueue(self, item):
        """Add item to rear - O(1)"""
        if self.count >= self.capacity:
            raise Exception(f"Queue is full (capacity: {self.capacity})")
        self.rear = (self.rear + 1) % self.capacity
        self.items[self.rear] = item
        self.count += 1
        return True
    
    def dequeue(self):
        """Remove item from front - O(1)"""
        if self.count == 0:
            return None
        item = self.items[self.front]
        self.items[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return item
    
    def peek(self):
        """View front item without removing - O(1)"""
        if self.count == 0:
            return None
        return self.items[self.front]
    
    def is_empty(self):
        """Check if queue is empty - O(1)"""
        return self.count == 0
    
    def size(self):
        """Get number of items - O(1)"""
        return self.count
    
    def get_all(self):
        """Get all items in order (front to rear) - O(n)"""
        if self.count == 0:
            return []
        result = []
        index = self.front
        for _ in range(self.count):
            result.append(self.items[index])
            index = (index + 1) % self.capacity
        return result
    
    def clear(self):
        """Clear all items"""
        for i in range(self.capacity):
            self.items[i] = None
        self.front = 0
        self.rear = -1
        self.count = 0
    
    def __len__(self):
        return self.count
    
    def __str__(self):
        return f"Queue(size={self.count}, capacity={self.capacity})"


# ============================================
# 6. HASH NODE CLASS - For hash table
# ============================================
class HashNode:
    """Node for hash table chaining"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


# ============================================
# 7. HASH TABLE CLASS - Replaces dictionary
# ============================================
class HashTable:
    """
    Hash table implementation with chaining for collision resolution
    Used for: zones, vehicles, requests storage (replaces Python dict)
    """
    
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.size = 0
        self.buckets = [None] * capacity
    
    def _hash(self, key):
        """Hash function - O(1)"""
        # Convert key to string and sum character codes
        key_str = str(key)
        hash_value = 0
        for char in key_str:
            hash_value += ord(char)
        return hash_value % self.capacity
    
    def insert(self, key, value):
        """Insert or update key-value pair - O(1) average"""
        index = self._hash(key)
        
        # Check if key already exists and update
        current = self.buckets[index]
        while current:
            if current.key == key:
                current.value = value
                return True
            current = current.next
        
        # Insert new node at beginning of chain
        new_node = HashNode(key, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.size += 1
        return True
    
    def get(self, key):
        """Get value for key - O(1) average"""
        index = self._hash(key)
        current = self.buckets[index]
        
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return None
    
    def delete(self, key):
        """Delete key-value pair - O(1) average"""
        index = self._hash(key)
        current = self.buckets[index]
        prev = None
        
        while current:
            if current.key == key:
                if prev:
                    prev.next = current.next
                else:
                    self.buckets[index] = current.next
                self.size -= 1
                return True
            prev = current
            current = current.next
        return False
    
    def contains(self, key):
        """Check if key exists - O(1) average"""
        return self.get(key) is not None
    
    def keys(self):
        """Get all keys - O(n)"""
        result = []
        for bucket in self.buckets:
            current = bucket
            while current:
                result.append(current.key)
                current = current.next
        return result
    
    def values(self):
        """Get all values - O(n)"""
        result = []
        for bucket in self.buckets:
            current = bucket
            while current:
                result.append(current.value)
                current = current.next
        return result
    
    def items(self):
        """Get all key-value pairs as list of tuples - O(n)"""
        result = []
        for bucket in self.buckets:
            current = bucket
            while current:
                result.append((current.key, current.value))
                current = current.next
        return result
    
    def clear(self):
        """Clear all items"""
        self.buckets = [None] * self.capacity
        self.size = 0
    
    def __len__(self):
        return self.size
    
    def __contains__(self, key):
        return self.contains(key)
    
    def __str__(self):
        return f"HashTable(size={self.size}, capacity={self.capacity})"


# ============================================
# 8. ADJACENCY NODE CLASS - For zone graph
# ============================================
class AdjacencyNode:
    """Node for adjacency list"""
    def __init__(self, zone_id):
        self.zone_id = zone_id
        self.next = None


# ============================================
# 9. ADJACENCY LIST CLASS - For zone relationships
# ============================================
class AdjacencyList:
    """
    Custom adjacency list for zone relationships (graph structure)
    Used for: Representing adjacent zones in the city
    """
    
    def __init__(self):
        self.head = None
        self.count = 0
    
    def add_adjacent_zone(self, zone_id):
        """Add adjacent zone - O(n)"""
        # Check if already exists
        if self.is_adjacent(zone_id):
            return False
        
        # Insert at beginning
        new_node = AdjacencyNode(zone_id)
        new_node.next = self.head
        self.head = new_node
        self.count += 1
        return True
    
    def remove_adjacent_zone(self, zone_id):
        """Remove adjacent zone - O(n)"""
        if not self.head:
            return False
        
        # If head contains zone_id
        if self.head.zone_id == zone_id:
            self.head = self.head.next
            self.count -= 1
            return True
        
        # Search in rest
        current = self.head
        while current.next:
            if current.next.zone_id == zone_id:
                current.next = current.next.next
                self.count -= 1
                return True
            current = current.next
        return False
    
    def is_adjacent(self, zone_id):
        """Check if zone is adjacent - O(n)"""
        current = self.head
        while current:
            if current.zone_id == zone_id:
                return True
            current = current.next
        return False
    
    def get_adjacent_zones(self):
        """Get list of all adjacent zone IDs - O(n)"""
        result = []
        current = self.head
        while current:
            result.append(current.zone_id)
            current = current.next
        return result
    
    def clear(self):
        """Clear all adjacent zones"""
        self.head = None
        self.count = 0
    
    def __len__(self):
        return self.count
    
    def __iter__(self):
        """Make adjacency list iterable"""
        current = self.head
        while current:
            yield current.zone_id
            current = current.next
    
    def __str__(self):
        return f"AdjacencyList(count={self.count}, zones={self.get_adjacent_zones()})"
