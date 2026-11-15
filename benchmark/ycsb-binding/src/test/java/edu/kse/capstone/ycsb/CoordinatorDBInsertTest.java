package edu.kse.capstone.ycsb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;
import java.util.Properties;
import java.util.UUID;
import java.util.HashMap;

import site.ycsb.ByteIterator;
import site.ycsb.Status;
import site.ycsb.StringByteIterator;

import static org.junit.jupiter.api.Assertions.*;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

class CoordinatorDBInsertTest {

    @Test
    void insertCreatesRecordInCoordinator() throws Exception {
        String baseUrl = System.getenv("COORDINATOR_URL");

        assumeTrue(
                baseUrl != null && !baseUrl.isBlank(),
                "Set COORDINATOR_URL to run integration tests"
        );

        HttpClient client = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .build();
        ObjectMapper json = new ObjectMapper();

        String table = "ycsb_test_" +
                UUID.randomUUID().toString().replace("-", "");

        String tableBody = json.writeValueAsString(Map.of(
                "name", table,
                "partition_key", "id"
        ));

        HttpRequest createTable = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/tables"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(tableBody))
                .build();

        HttpResponse<String> tableResponse = client.send(
                createTable,
                HttpResponse.BodyHandlers.ofString()
        );

        assertEquals(
                201,
                tableResponse.statusCode(),
                "Coordinator response: " + tableResponse.body()
        );

        CoordinatorDB db = new CoordinatorDB();

        Properties properties = new Properties();
        properties.setProperty("coordinator.url", baseUrl);

        db.setProperties(properties);
        db.init();

        Map<String, ByteIterator> values = Map.of(
                "name", new StringByteIterator("Anna"),
                "subject", new StringByteIterator("Math")
        );

        Status status = db.insert(table, "student101", values);

        assertEquals(Status.OK, status);

        HttpRequest readRequest = HttpRequest.newBuilder()
                .uri(URI.create(
                        baseUrl + "/tables/" + table +
                        "/records/student101"
                ))
                .GET()
                .build();

        HttpResponse<String> readResponse = client.send(
                readRequest,
                HttpResponse.BodyHandlers.ofString()
        );

        assertEquals(200, readResponse.statusCode());

        JsonNode record = json.readTree(readResponse.body());

        assertEquals("student101", record.get("key").asText());
        assertEquals("Anna", record.get("value").get("name").asText());
        assertEquals("Math", record.get("value").get("subject").asText());

        Map<String, ByteIterator> readResult = new HashMap<>();

        Status readStatus = db.read(
                table,
                "student101",
                null,
                readResult
        );

        assertEquals(Status.OK, readStatus);
        assertEquals("Anna", readResult.get("name").toString());
        assertEquals("Math", readResult.get("subject").toString());

        Status missingStatus = db.read(
                table,
                "nonexistent-student",
                null,
                new HashMap<>()
        );

        assertEquals(Status.NOT_FOUND, missingStatus);

        System.out.println("YCSB READ integration test passed");

        System.out.println("YCSB INSERT integration test passed");


        Map<String, ByteIterator> updatedValues = Map.of(
                "name", new StringByteIterator("Anna"),
                "subject", new StringByteIterator("Physics")
        );

        Status updateStatus = db.update(
                table,
                "student101",
                updatedValues
        );

        assertEquals(Status.OK, updateStatus);

        Map<String, ByteIterator> updatedResult = new HashMap<>();

        Status updatedReadStatus = db.read(
                table,
                "student101",
                null,
                updatedResult
        );

        assertEquals(Status.OK, updatedReadStatus);
        assertEquals("Anna", updatedResult.get("name").toString());
        assertEquals("Physics", updatedResult.get("subject").toString());

        System.out.println("YCSB UPDATE integration test passed");

        Status deleteStatus = db.delete(
                table,
                "student101"
        );

        assertEquals(Status.OK, deleteStatus);

        Map<String, ByteIterator> deletedResult = new HashMap<>();

        Status deletedReadStatus = db.read(
                table,
                "student101",
                null,
                deletedResult
        );

        assertEquals(Status.NOT_FOUND, deletedReadStatus);

        Status secondDeleteStatus = db.delete(
                table,
                "student101"
        );

        assertEquals(Status.NOT_FOUND, secondDeleteStatus);

        System.out.println("YCSB DELETE integration test passed");


    }
}