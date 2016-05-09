package prodcon;


public class StreamingApp {
	/*
	 * <TamanhoDoBuffer> <TamanhoDoBloco> <TaxaDeStream> 
	 * <BlocoDeTroca> <NomeDoArquivo1> <NomeDoArquivo2>
	 */

	public static void main(String[] args) {

		Integer bufferSize = Integer.parseInt(args[0]);
		Integer blockSize = Integer.parseInt(args[1]);
		Integer streamRate = Integer.parseInt(args[2]);
		Integer changeBlock = Integer.parseInt(args[3]);
		ProdCon prodcon;

		String firstObj = args[4];

		if (changeBlock != 0 ) {
			String secondObj = args[5];
			prodcon = new ProdCon(bufferSize, blockSize, streamRate, changeBlock, firstObj, secondObj);
		}
		else {
			prodcon = new ProdCon(bufferSize, blockSize, streamRate, firstObj);
		}
	}
}

