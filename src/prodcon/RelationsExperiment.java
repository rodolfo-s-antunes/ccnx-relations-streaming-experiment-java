package prodcon;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.*;

public class RelationsExperiment {

	/*
	 * Formato do arquivo:
	 * <nome> 
	 * <objetoVideo> <TamanhoBlocoVideo> <TamanhoBufferVideo> <TaxaStreamVideo> 
	 * <audioID> <TamanhoBlocoAudio> <TamanhoBufferAudio> <TaxaStreamAudio>
	 */

	public static void main(String[] args) {

		Vector<RelationsClientInstance> clients = new Vector<RelationsClientInstance>();
		parseClientFile(args[0], clients);
		for (RelationsClientInstance ci : clients)
			ci.start();
		try {
			for (RelationsClientInstance ci : clients)
				ci.join();
		} catch (Exception exc) {exc.printStackTrace();}
		System.exit(0);
	}

	public static void parseClientFile(String arqname, Vector<RelationsClientInstance> clients) {
		try {
			BufferedReader arqin = new BufferedReader(new FileReader(arqname));
			boolean kr = true;
			while (kr) {
				String linha = arqin.readLine();
				if (linha == null) {kr = false;}
				else {
					System.out.println(linha);
					String[] auxQ = linha.split(" ");
					RelationsClientInstance bci = new RelationsClientInstance(
							auxQ[0],
							auxQ[1],
							Integer.parseInt(auxQ[2]),
							Integer.parseInt(auxQ[3]),
							Integer.parseInt(auxQ[4]),
							auxQ[5],
							Integer.parseInt(auxQ[6]),
							Integer.parseInt(auxQ[7]),
							Integer.parseInt(auxQ[8]),
							Long.parseLong(auxQ[9]));
					clients.add(bci);
				}
			}
			arqin.close();
		} catch (Exception exc) {
			System.out.println("Error trying to read node list file");
			exc.printStackTrace();
		}
	}

}
