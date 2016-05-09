package prodcon;

import org.ccnx.ccn.CCNHandle;
import org.ccnx.ccn.config.ConfigurationException;
import org.ccnx.ccn.io.CCNFileInputStream;
import org.ccnx.ccn.io.CCNInputStream;
import org.ccnx.ccn.protocol.ContentName;
import org.ccnx.ccn.protocol.MalformedContentNameStringException;

public class Producer extends Thread {
	private Buffer buffer;
	private String filename, name;
	private long begins, ends;
	private int blocksize;

	public Producer(String name, String filename, int blocksize, long begins, long ends, Buffer buffer) {
		this.buffer = buffer;
		this.name = name;
		this.filename = filename;
		this.begins = begins;
		this.ends = ends;
		this.blocksize = blocksize;
	}

	public void run() {
		try {
			ContentName ccnname = ContentName.fromURI(filename);
			CCNHandle ccnhandle = CCNHandle.open();
			CCNInputStream input = new CCNFileInputStream(ccnname, ccnhandle);
			if (begins > 0)
				input.skip(blocksize*begins);
			long count = begins;
			do {
				long getbegin = System.nanoTime();
				byte[] temp = new byte[blocksize];
				long getprod = System.nanoTime();
				System.out.format("%s: recovered block %d after %d ns.\n", name, count, getprod-getbegin);
				int res = input.read(temp);
				count += 1;
				if (res < blocksize || ends > 0 && count == ends) {
					buffer.finish.set(true);
				}
				if (res > 0) {
					buffer.put(prim2obj(temp,res));
					
				}
				if (res < 0 && buffer.finish.get()) {
					buffer.signalFinish();
				}
				long getend = System.nanoTime();
				System.out.format("%s: produced block %d after %d ns.\n", name, count, getend-getbegin);
			} while (!buffer.finish.get());
			input.close();
			System.out.format("%s: Producer finished.\n", name);
		} catch (ConfigurationException e) {
			System.out.format("%s: configuration exception: %s", name, e.getMessage());
			e.printStackTrace();
		} catch (MalformedContentNameStringException e) {
			System.out.format("%s: malformed name: %s %s", name, filename, e.getMessage());
			e.printStackTrace();
		} catch (Exception e) {
			buffer.finish.set(true);
			try {buffer.put(new Byte[0]);}
			catch (Exception exc) {exc.printStackTrace();}
			System.out.format("%s: Exception at the producer!\n", name);
			e.printStackTrace();
		}
	}

	private Byte[] prim2obj(byte[] data, int howmany) {
		Byte[] result = new Byte[howmany];
		for (int i=0; i<howmany; i++) {
			result[i] = data[i];
		}
		return result;
	}

}
