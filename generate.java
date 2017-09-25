import java.util.*;
import java.io.*;

public class generate {
	public static void main(String args[]) throws IOException {
		Scanner diseaseFile = new Scanner(new File("diagnosis.txt"));
		ArrayList <String> diseases = new ArrayList <String> ();
		ArrayList <String> symptoms = new ArrayList <String> ();
		while (diseaseFile.hasNext()) {
			diseases.add(diseaseFile.nextLine());
		}
		diseaseFile.close();
		Scanner symptomFile = new Scanner(new File("symptoms.txt")); 
		while (symptomFile.hasNext()) {
			String symptom = symptomFile.nextLine();
			symptoms.add(symptom);
		}
		symptomFile.close();
		Map <String, TreeSet <String>> data = new TreeMap <String, TreeSet <String>>();
		for (String disease : diseases) {
			TreeSet <String> diseaseSymptoms = new TreeSet <String> ();
			for (String symptom : symptoms) {
				double roll = Math.random();
				if (roll >= 0.5) {
					diseaseSymptoms.add(symptom);
				}
				data.put(disease, diseaseSymptoms);
			}
		}
		Map <String, TreeSet <String>> invertedData = new TreeMap <String, TreeSet <String>> ();

		for (String disease : data.keySet()) {
			String output = "\"" + disease + "\": [";
			for (String symptom : data.get(disease)) {
				output += "\"" + symptom + "\",";
				if (invertedData.get(symptom) == null) {
					TreeSet <String> symptomDiseases = new TreeSet <String>();
					symptomDiseases.add(disease);
					invertedData.put(symptom, symptomDiseases);
				}
				else {
					invertedData.get(symptom).add(disease);
				}
			}
			System.out.println(output.substring(0, output.length() - 1) + "],");
		}

		System.out.println();

		for (String symptom : invertedData.keySet()) {
			String output = "\"" + symptom +"\": [";
			for (String disease : invertedData.get(symptom)) {
				output += "\"" + disease + "\",";
			}
			System.out.println(output.substring(0, output.length() - 1) + "],");
		}
		System.out.println();
	}
}