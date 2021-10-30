

/// Result of some transaction with a [ReorderBuffer].
pub enum RingBufferResult<E> {
    /// Successfully pushed entry into the buffer at some index.
    Pushed(usize),
    /// Successfully popped entry from buffer at some index.
    Popped(E, usize),
    /// Failed to pop entry from the buffer (the buffer is empty).
    Empty,
    /// Failed to push entry into the buffer (the buffer is full).
    Full,
}

/// A circular buffer.
pub struct RingBuffer<E> {
    data: Vec<Option<E>>,
    head: usize,
    tail: usize,
    size: usize,
}
impl RingBuffer<E> {
    pub fn new(size: usize) -> Self {
        Self {
            size,
            head: 0, 
            tail: size - 1,
            data: Vec::with_capacity(size),
        }
    }
    pub fn push(&mut self, e: E) -> RingBufferResult<E> {
        if (self.head == self.tail) && (self.data[self.head].is_some()) {
            ROBResult::Full
        } else {
            let tail = self.tail;
            self.data[self.tail] = Some(e);
            self.tail = (self.tail + 1) % self.size;
            RingBufferResult::Pushed(tail)
        }
    }
    pub fn pop(&mut self) -> RingBufferResult<E> {
        if self.data[self.head].is_none() {
            RingBufferResult::Empty
        } else {
            let head = self.head;
            let res = self.data[self.head].take().unwrap();
            self.head = (self.head + 1) % self.size;
            RingBufferResult::Popped(res, head)
        }
    }
}


