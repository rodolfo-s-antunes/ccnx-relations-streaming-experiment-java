package prodcon;

public class BasicClientInstance extends Thread {
	private String name, object;
	private int bufferSize, blockSize, streamRate;
	private long beginTime;

	public BasicClientInstance(
			String name,
			String object,
			int blockSize,
			int bufferSize,
			int streamRate,
			long beginTime) {
		this.name = name;
		this.object = object;
		this.blockSize = blockSize;
		this.bufferSize = bufferSize;
		this.streamRate = streamRate;
		this.beginTime = beginTime;
	}

	public void run() {
		System.out.format("Start in %d seconds...\n", beginTime);
		try {
			Thread.sleep(beginTime * 1000L);
		} catch(InterruptedException ex) {
			Thread.currentThread().interrupt();
		}
		System.out.format("name=%s object=%s bufferSize=%d blockSize=%d streamRate=%d\n", name, object, bufferSize, blockSize, streamRate);
		Buffer buffer = new Buffer(name, bufferSize);
		Producer producer = new Producer(name, object, blockSize, 0, 0, buffer);
		Consumer consumer = new Consumer(name, 0, 0, buffer, streamRate);
		producer.start();
		consumer.start();
		try {
			producer.join();
			consumer.join();
		} catch (Exception exc) {
			System.out.format("Exception at Client %s!\n", name);
			exc.printStackTrace();
		}
	}

}
