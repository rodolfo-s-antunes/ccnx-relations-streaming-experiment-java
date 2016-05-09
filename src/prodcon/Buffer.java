package prodcon;

import java.util.*;
import java.util.concurrent.locks.*;
import java.util.concurrent.atomic.AtomicBoolean;

public class Buffer {
	private LinkedList<Byte[]> buffer;
	private long capacity;
	private String name;
	public AtomicBoolean finish, isempty, stalled;

	private final Lock lock = new ReentrantLock();
	private final Condition notFull = lock.newCondition();
	private final Condition notEmpty = lock.newCondition();

	public Buffer(String name, long capacity) {
		this.name = name;
		this.capacity = capacity;
		reset();
	}
	
	public void reset() {
		this.buffer = new LinkedList<Byte[]>();
		this.finish = new AtomicBoolean(false);
		this.stalled = new AtomicBoolean(false);
		this.isempty = new AtomicBoolean(true);
	}
	
	public void signalFinish() {
		stalled.set(false);
		notEmpty.signal();
	}

	public void put(Byte[] data) throws InterruptedException {
		lock.lock();
		try {
			while (buffer.size() == capacity) {
				notFull.await();
			}
			buffer.add(data);
			if (isempty.get()) isempty.set(false);
			if (finish.get() || stalled.get() && buffer.size() == capacity) {
				stalled.set(false);
				notEmpty.signal();
			}
		} finally {
			lock.unlock();
		}
	}

	public Byte[] get() throws InterruptedException {
		lock.lock();
		try {
			while (buffer.isEmpty()) {
				System.out.format("%s: Buffer is empty! Awating for it to fill.\n", name);
				stalled.set(true);
				long begintime = System.nanoTime();
				notEmpty.await();	
				long endtime = System.nanoTime();
				System.out.format("%s: Buffer filled! Lock released.\n", name);
				System.out.format("%s: Waiting time until filled: %d ns.\n", name, endtime-begintime);
			}
			Byte[] result = buffer.pop();
			if (buffer.isEmpty()) isempty.set(true);
			notFull.signal();
			return result;
		} finally {
			lock.unlock();
		}
	}
}
