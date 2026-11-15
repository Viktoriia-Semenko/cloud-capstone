package edu.kse.capstone.ycsb;

import java.net.http.HttpClient;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.Vector;

import site.ycsb.ByteIterator;
import site.ycsb.DB;
import site.ycsb.DBException;
import site.ycsb.Status;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import com.fasterxml.jackson.databind.JsonNode;
import site.ycsb.StringByteIterator;


public class CoordinatorDB extends DB {
    private static final ObjectMapper JSON = new ObjectMapper();

    private String coordinatorUrl;
    private HttpClient httpClient;

    @Override
    public void init() throws DBException {
        super.init();

        coordinatorUrl = getProperties()
                .getProperty("coordinator.url");

        if (coordinatorUrl == null || coordinatorUrl.isBlank()) {
            throw new DBException(
                    "Missing required property: coordinator.url"
            );
        }

        coordinatorUrl = coordinatorUrl.replaceAll("/+$", "");

        httpClient = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(Duration.ofSeconds(5))
                .build();
    }

    
    @Override
    public Status read(
            String table,
            String key,
            Set<String> fields,
            Map<String, ByteIterator> result) {

        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(
                            coordinatorUrl + "/tables/" + table +
                            "/records/" + key
                    ))
                    .timeout(Duration.ofSeconds(15))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(
                    request,
                    HttpResponse.BodyHandlers.ofString()
            );

            if (response.statusCode() == 404) {
                return Status.NOT_FOUND;
            }

            if (response.statusCode() == 503) {
                return Status.SERVICE_UNAVAILABLE;
            }

            if (response.statusCode() != 200) {
                return Status.ERROR;
            }

            JsonNode record = JSON.readTree(response.body());
            JsonNode values = record.path("value");

            if (!values.isObject()) {
                return Status.ERROR;
            }

            result.clear();

            values.fields().forEachRemaining(entry -> {
                String fieldName = entry.getKey();

                if (fields == null || fields.contains(fieldName)) {
                    result.put(
                            fieldName,
                            new StringByteIterator(entry.getValue().asText())
                    );
                }
            });

            return Status.OK;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return Status.ERROR;

        } catch (IOException | IllegalArgumentException e) {
            System.err.println("YCSB READ failed: " + e.getMessage());
            return Status.ERROR;
        }
    }


    @Override
    public Status scan(
            String table,
            String startkey,
            int recordcount,
            Set<String> fields,
            Vector<HashMap<String, ByteIterator>> result) {

        return Status.NOT_IMPLEMENTED;
    }

    
    @Override
    public Status update(
            String table,
            String key,
            Map<String, ByteIterator> values) {

        try {
            Map<String, String> fields = new LinkedHashMap<>();

            for (Map.Entry<String, ByteIterator> entry : values.entrySet()) {
                fields.put(
                        entry.getKey(),
                        entry.getValue().toString()
                );
            }

            Map<String, Object> body = Map.of(
                    "value", fields
            );

            String json = JSON.writeValueAsString(body);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(
                            coordinatorUrl + "/tables/" + table +
                            "/records/" + key
                    ))
                    .header("Content-Type", "application/json")
                    .timeout(Duration.ofSeconds(15))
                    .PUT(HttpRequest.BodyPublishers.ofString(
                            json, StandardCharsets.UTF_8
                    ))
                    .build();

            HttpResponse<String> response = httpClient.send(
                    request,
                    HttpResponse.BodyHandlers.ofString()
            );

            if (response.statusCode() == 200) {
                return Status.OK;
            }

            if (response.statusCode() == 404) {
                return Status.NOT_FOUND;
            }

            if (response.statusCode() == 503) {
                return Status.SERVICE_UNAVAILABLE;
            }

            if (response.statusCode() == 400 ||
                    response.statusCode() == 422) {
                return Status.BAD_REQUEST;
            }

            return Status.ERROR;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return Status.ERROR;

        } catch (IOException | IllegalArgumentException e) {
            System.err.println("YCSB UPDATE failed: " + e.getMessage());
            return Status.ERROR;
        }
    }


    @Override
    public Status insert(
            String table,
            String key,
            Map<String, ByteIterator> values) {

        try {
            Map<String, String> fields = new LinkedHashMap<>();

            for (Map.Entry<String, ByteIterator> entry : values.entrySet()) {
                fields.put(entry.getKey(), entry.getValue().toString());
            }

            Map<String, Object> record = Map.of(
                    "key", key,
                    "value", fields
            );

            String json = JSON.writeValueAsString(record);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(
                            coordinatorUrl + "/tables/" + table + "/records"
                    ))
                    .header("Content-Type", "application/json")
                    .timeout(Duration.ofSeconds(15))
                    .POST(HttpRequest.BodyPublishers.ofString(
                            json, StandardCharsets.UTF_8
                    ))
                    .build();

            HttpResponse<String> response = httpClient.send(
                    request,
                    HttpResponse.BodyHandlers.ofString()
            );

            if (response.statusCode() == 201) {
                return Status.OK;
            }

            if (response.statusCode() == 400 ||
                    response.statusCode() == 422) {
                return Status.BAD_REQUEST;
            }

            if (response.statusCode() == 503) {
                return Status.SERVICE_UNAVAILABLE;
            }

            return Status.ERROR;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return Status.ERROR;

        } catch (IOException | IllegalArgumentException e) {
            System.err.println("YCSB INSERT failed: " + e.getMessage());
            return Status.ERROR;
        }
    }


    @Override
    public Status delete(String table, String key) {

        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(
                            coordinatorUrl + "/tables/" + table +
                            "/records/" + key
                    ))
                    .timeout(Duration.ofSeconds(15))
                    .DELETE()
                    .build();

            HttpResponse<String> response = httpClient.send(
                    request,
                    HttpResponse.BodyHandlers.ofString()
            );

            if (response.statusCode() == 204) {
                return Status.OK;
            }

            if (response.statusCode() == 404) {
                return Status.NOT_FOUND;
            }

            if (response.statusCode() == 503) {
                return Status.SERVICE_UNAVAILABLE;
            }

            return Status.ERROR;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return Status.ERROR;

        } catch (IOException | IllegalArgumentException e) {
            System.err.println("YCSB DELETE failed: " + e.getMessage());
            return Status.ERROR;
        }
    }

}
