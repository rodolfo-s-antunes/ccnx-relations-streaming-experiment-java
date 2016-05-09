package prodcon;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.*;

public class BasicExperiment {

	/*
	 * Formato do arquivo:
	 * <nome> <objeto> <TamanhoBloco> <TamanhoBuffer> <TaxaStream>
	 */

	public static void main(String[] args) {

		Vector<BasicClientInstance> clients = new Vector<BasicClientInstance>();
		
		parseClientFile(args[0], clients);
		
		for (BasicClientInstance ci : clients)
			ci.start();
		try {
			for (BasicClientInstance ci : clients)
				ci.join();
		} catch (Exception exc) {exc.printStackTrace();}
		System.exit(0);
	}

	public static void parseClientFile(String arqname, Vector<BasicClientInstance> clients) {
		try {
			BufferedReader arqin = new BufferedReader(new FileReader(arqname));
			boolean kr = true;
			while (kr) {
				String linha = arqin.readLine();
				if (linha == null) {kr = false;}
				else {
					System.out.println(linha);
					String[] auxQ = linha.split(" ");
					BasicClientInstance bci = new BasicClientInstance(
							auxQ[0],
							auxQ[1],
							Integer.parseInt(auxQ[2]),
							Integer.parseInt(auxQ[3]),
							Integer.parseInt(auxQ[4]),
							Long.parseLong(auxQ[5]));
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
