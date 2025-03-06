package org.example;

import java.io.*;
import java.nio.charset.StandardCharsets;
import org.apache.commons.csv.*;
import org.json.JSONObject;

public class StudentInfoFetcher {
    private static final String CSV_FILE_PATH = "/students.csv"; // Resource path

    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("{\"error\": \"Usage: java -jar student_info_fetcher.jar <studentID>\"}");
            return;
        }

        String studentID = args[0];
        JSONObject studentData = findStudentById(studentID);

        if (studentData != null) {
            System.out.println(studentData.toString(4)); // Pretty-print JSON
        } else {
            System.out.println("{\"error\": \"Student ID not found\"}");
        }
    }

    private static JSONObject findStudentById(String studentID) {
        try (InputStream inputStream = StudentInfoFetcher.class.getResourceAsStream(CSV_FILE_PATH);
             Reader reader = new InputStreamReader(inputStream, StandardCharsets.UTF_8);
             CSVParser csvParser = new CSVParser(reader,
                     CSVFormat.DEFAULT
                             .withFirstRecordAsHeader() // Skip header row
                             .withQuote('"')  // ✅ Correctly handles quoted fields (e.g., addresses)
                             .withIgnoreSurroundingSpaces(true))) {

            for (CSVRecord record : csvParser) {
                if (record.get("id").equals(studentID)) {
                    JSONObject student = new JSONObject();
                    student.put("studentID", record.get("id"));
                    student.put("Name", record.get("name"));
                    student.put("Age", Integer.parseInt(record.get("age")));
                    student.put("Address", record.get("address"));
                    student.put("Major", record.get("major"));
                    return student;
                }
            }
        } catch (Exception e) {
            System.err.println("Error reading CSV file: " + e.getMessage());
        }
        return null;
    }
}
