package prodcon;

import java.util.*;

public class RelationsClientInstance extends Thread {
	private String name, objectVideo, audioID;
	private int blockSizeVideo, bufferSizeVideo, streamRateVideo, 
				blockSizeAudio, bufferSizeAudio, streamRateAudio;
	private String objectAudio;
	private long beginTime;

	public RelationsClientInstance(
			String name,
			String objectVideo,
			int blockSizeVideo,
			int bufferSizeVideo,
			int streamRateVideo,
			String audioID,
			int blockSizeAudio,
			int bufferSizeAudio,
			int streamRateAudio,
			long beginTime) {
		this.name = name;
		this.objectVideo = objectVideo;
		this.blockSizeVideo = blockSizeVideo;
		this.bufferSizeVideo = bufferSizeVideo;
		this.streamRateVideo = streamRateVideo;
		this.audioID = audioID;
		this.blockSizeAudio = blockSizeAudio;
		this.bufferSizeAudio = bufferSizeAudio;
		this.streamRateAudio = streamRateAudio;
		this.beginTime = beginTime;
	}

	public void run() {
			System.out.format("Start in %d seconds...\n", beginTime);
			try {
			    Thread.sleep(beginTime * 1000L);
			} catch(InterruptedException ex) {
			    Thread.currentThread().interrupt();
			}
		Hashtable<String, String> h = CCNRelations.getRelations(objectVideo, "relations"); 
		objectAudio = CCNRelations.getObjectName(h, audioID);
		System.out.format("name=%s objectVideo=%s blockSizeVideo=%d bufferSizeVideo=%d streamRateVideo=%d audioID=%s blockSizeAudio=%d bufferSizeAudio=%d streamRateAudio=%d \n", name, objectVideo, blockSizeVideo, bufferSizeVideo, streamRateVideo, audioID, blockSizeAudio, bufferSizeAudio, streamRateAudio);
		//video
		Buffer bufferVideo = new Buffer(name+"Video", bufferSizeVideo);
		Producer producerVideo = new Producer(name+"Video", objectVideo, blockSizeVideo, 0, 0, bufferVideo);
		Consumer consumerVideo = new Consumer(name+"Video", 0, 0, bufferVideo, streamRateVideo);
		//audio
		Buffer bufferAudio = new Buffer(name+"Audio", bufferSizeAudio);
		Producer producerAudio = new Producer(name+"Audio", objectAudio, blockSizeAudio, 0, 0, bufferAudio);
		Consumer consumerAudio = new Consumer(name+"Audio", 0, 0, bufferAudio, streamRateAudio);
		//threads
		producerVideo.start();
		consumerVideo.start();
		producerAudio.start();
		consumerAudio.start();
		try {
			producerVideo.join();
			consumerVideo.join();
			producerAudio.join();
			consumerAudio.join();
		} catch (Exception exc) {
			System.out.format("Exception at Client %s!\n", name);
			exc.printStackTrace();
		}
	}
}
