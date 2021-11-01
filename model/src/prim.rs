
/// A name/index for an architectural register.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(transparent)]
pub struct ArchReg(pub usize);



#[derive(Debug)]
pub struct RingBuffer<E> where E: Clone + Copy + std::fmt::Debug {
    data: Vec<Option<E>>,
    head: usize,
    tail: usize,
    size: usize,
}
impl <E: Clone + Copy + std::fmt::Debug> RingBuffer<E> {
    pub fn new(size: usize) -> Self {
        Self {
            size,
            head: 0, 
            tail: 0,
            data: vec![None; size],
        }
    }
    pub fn is_full(&self) -> bool {
        (self.head == self.tail) && self.data[self.head].is_some()
    }
    pub fn is_empty(&self) -> bool {
        self.data[self.head].is_none()
    }
    pub fn push(&mut self, e: E) -> Option<usize> {
        if (self.head == self.tail) && (self.data[self.head].is_some()) {
            None
        } else {
            let tail = self.tail;
            self.data[self.tail] = Some(e);
            self.tail = (self.tail + 1) % self.size;
            Some(tail)
        }
    }
    pub fn pop(&mut self) -> Option<(E, usize)> {
        if self.data[self.head].is_none() {
            None
        } else {
            let head = self.head;
            let res = self.data[self.head].take().unwrap();
            self.head = (self.head + 1) % self.size;
            Some((res, head))
        }
    }
    pub fn get(&self, idx: usize) -> &Option<E> {
        assert!(idx < self.size - 1);
        &self.data[idx]
    }
    pub fn get_mut(&mut self, idx: usize) -> &mut Option<E> {
        assert!(idx < self.size - 1);
        &mut self.data[idx]
    }
}


