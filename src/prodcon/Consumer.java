package prodcon;

public class Consumer extends Thread {
	private Buffer buffer;
	private String name;
	private long begins, ends;
	private long stepmillis;
	private int stepnanos;

	public Consumer(String name, long begins, long ends, Buffer buffer, long rate) {
		this.buffer = buffer;
		this.begins = begins;
		this.ends = ends;
		this.name = name;
		calcrates(rate);
	}

	private void calcrates(long rate) {
		long baserate = 1000000000/rate;
		stepmillis = baserate/1000000;
		stepnanos =  (int) baserate%1000000;
		System.out.format("%s: steps: millis=%d nanos=%d\n", name, stepmillis, stepnanos);
	}

	public void run() {
		try {
			long count = begins;
			while (true) {
				long consumerbegin = System.nanoTime();
				buffer.get();
				long consumerend = System.nanoTime();
				count += 1;
				System.out.format("%s: consumed block %d after %d ns.\n", name, count, consumerend-consumerbegin);
				if (buffer.finish.get() && buffer.isempty.get()) break;
				sleep(stepmillis, stepnanos);
			}
			System.out.format("%s: Consumer finished.\n", name);
		} catch (Exception e) {
			System.out.format("%s: Exception at the consumer!\n", name);
			e.printStackTrace();
		}
	}
}
