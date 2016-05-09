package prodcon;

public class ProdCon {

	String name = "VIDEO";
	
	public ProdCon (Integer bufferSize, Integer blockSize,  
			Integer streamRate, Integer changeBlock, String object1, String object2) {
		Buffer buffer = new Buffer(name, bufferSize);
		Producer prod = new Producer(name, object1, blockSize, 0, changeBlock, buffer);
		Consumer con = new Consumer(name, 0, changeBlock, buffer, streamRate);
		prod.start();
		con.start();
		try {
			prod.join();
			con.join();
		}
		catch (Exception exc) { exc.printStackTrace(); 	}
		
		buffer.reset();
		prod = new Producer(name, object2, blockSize, changeBlock, 0, buffer);
		con = new Consumer(name, changeBlock, 0, buffer, streamRate);
		prod.start();
		con.start();
		try {
			prod.join();
			con.join();
		}
		catch (Exception exc) { exc.printStackTrace(); 	}
		
		System.exit(0);
	}
	
	public ProdCon (Integer bufferSize, Integer blockSize,  
			Integer streamRate, String object1) {
		Buffer buffer = new Buffer(name, bufferSize);
		Producer prod = new Producer(name, object1, blockSize, 0, 0, buffer);
		Consumer con = new Consumer(name, 0, 0, buffer, streamRate);
		prod.start();
		con.start();
		try {
			prod.join();
			con.join();
		}
		catch (Exception exc) { exc.printStackTrace(); 	}
		System.exit(0);
	}

}
