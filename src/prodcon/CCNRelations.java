package prodcon;

import java.util.*;
import java.io.*;
import org.ccnx.ccn.CCNHandle;
import org.ccnx.ccn.config.ConfigurationException;
import org.ccnx.ccn.impl.support.Log;
import org.ccnx.ccn.io.CCNFileInputStream;
import org.ccnx.ccn.io.CCNInputStream;
import org.ccnx.ccn.profiles.VersioningProfile;
import org.ccnx.ccn.profiles.metadata.MetadataProfile;
import org.ccnx.ccn.protocol.ContentName;
import org.ccnx.ccn.protocol.MalformedContentNameStringException;
import org.ccnx.ccn.utils.*;

public class CCNRelations {

	public static Hashtable<String,String> getRelations(String ccnfilename, String metaname) {
		String metatemp = getMetaContent(ccnfilename, metaname);
		//Vector<String> l = parseMetaString("parent 1\tbla\nparent2\tbleh");
		Vector<String> l = parseMetaString(metatemp);
		Hashtable<String, String> h = convertToHash(l);
		return h;
	}

	public static String getObjectName(Hashtable<String,String> relations, String id) {
		return relations.get(id);
	}
	
	private static String getMetaContent(String ccnfilename, String metaname) {
		String metadata = new String();
		try {
			int readsize = 1024;
			CCNHandle handle = CCNHandle.open();
			if (!metaname.startsWith("/")) {
				metaname = "/" + metaname;
			}
			ContentName fileName = MetadataProfile.getLatestVersion(ContentName.fromURI(ccnfilename),
					ContentName.fromNative(metaname), CommonParameters.timeout, handle);
			if (fileName == null) { //file does not exist -> impossible to get metadata
				System.out.println("File " + ccnfilename + " does not exist");
				System.exit(1);
			}
			if (VersioningProfile.hasTerminalVersion(fileName)) {
				//MetadataProfile has found a terminal version...  we have something to get!
			} else {
				//MetadataProfile could not find a terminal version...  nothing to get
				System.out.println("File " + fileName + " does not exist...  exiting");
				System.exit(1);
			}

			CCNInputStream input;
			if (CommonParameters.unversioned)
				input = new CCNInputStream(fileName, handle);
			else
				input = new CCNFileInputStream(fileName, handle);

			byte [] buffer = new byte[readsize];
			int readcount = 0;
			//long readtotal = 0;
			while ((readcount = input.read(buffer)) != -1){
				//readtotal += readcount;
				metadata = metadata.concat(new String(buffer,0,readcount));
			}
		} catch (ConfigurationException e) {
			System.out.println("Configuration exception in ccngetfile: " + e.getMessage());
			e.printStackTrace();
		} catch (MalformedContentNameStringException e) {
			System.out.println("Malformed name: " + ccnfilename + " " + e.getMessage());
			e.printStackTrace();
		} catch (IOException e) {
			System.out.println("Cannot write file or read content. " + e.getMessage());
			e.printStackTrace();
		}

		return metadata;
	}
	
	private static Vector<String> parseMetaString(String name) 
	{
		Vector<String> result = new Vector<String>();
		String [] temp = name.split("\n"); 
		for (Integer i = 0; i < temp.length; i++) {
			result.add(temp[i]);
		}
		return result;
	}

	private static Hashtable<String,String> convertToHash(Vector<String> v) {
		Hashtable<String, String> h = new Hashtable<String, String>();
		for (Iterator<String> i = v.iterator(); i.hasNext();) {
			String [] temp = i.next().split("\t");
			h.put(temp[0], temp[1]);
		}
		return h;
	}


}
