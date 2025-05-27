package org.infai.hatespeechdetection;

import java.io.*;

import jakarta.json.*;
import jakarta.servlet.http.*;
import jakarta.servlet.annotation.*;

import org.provarules.kernel2.ProvaList;
import org.provarules.kernel2.ProvaObject;
import org.provarules.reference2.ProvaConstantImpl;
import org.provarules.reference2.ProvaListImpl;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

@WebServlet(value = "/legalcheck")
public class LegalEthicalCheckerIF extends HttpServlet {
    private final Logger logger = Logger.getLogger(getClass().getName());
    private static LegalEthicalChecker lec;

    @Override
    public void init() {
        if (lec == null) {
            lec = new LegalEthicalChecker();
        }
    }

    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        String region = request.getParameter("location");
        if (region == null) {
            response.sendError(HttpServletResponse.SC_BAD_REQUEST,"location parameter required");
            return;
        }
        lec.resetMessage();
        logger.info("Received location=" + region);
        lec.generateHasRegionLaws(request.getRequestId(), region);
        response.setContentType("application/json");
        response.getWriter().write(lec.getMessageToString());
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        lec.resetMessage();
        lec.resetComplexRules();
        JsonReader reader = Json.createReader(request.getInputStream());
        JsonObject root = reader.readObject();
        reader.close();

        String messageId = root.getString("message_id", null);
        String region    = root.getString("location", null);
        JsonObject tags  = root.getJsonObject("tags");

        logger.info("Received message_id=" + messageId + ", location=" + region);

        if (messageId == null || region == null) {
            response.sendError(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        response.setContentType("application/json");

        if (tags == null) {
            String message = lec.getMessageToString();
            response.getWriter().write(message);
            return;
        }

        // Map to hold parsed tag -> reasonsList
        Map<String, ProvaList> tagMap = new LinkedHashMap<>();

        // First loop: create one ProvaList per category
        for (String category : tags.keySet()) {
            JsonArray reasonsArray = tags.getJsonArray(category);
            if (reasonsArray == null || reasonsArray.isEmpty()) continue;

            ProvaObject[] reasonObjs = new ProvaObject[reasonsArray.size()];
            for (int i = 0; i < reasonsArray.size(); i++) {
                reasonObjs[i] = ProvaConstantImpl.create(reasonsArray.getString(i));
            }

            ProvaList reasonsList = ProvaListImpl.create(reasonObjs);

            // Execute simple rule
            ProvaObject[] termObjs = new ProvaObject[] {
                    ProvaConstantImpl.create(category),
                    reasonsList,
                    ProvaConstantImpl.create(region)
            };
            ProvaList terms = ProvaListImpl.create(termObjs);

            lec.executeSingleLegalQuery(messageId, terms);
            lec.executeSingleEthicalQuery(messageId, terms);
            tagMap.put(category, reasonsList);
        }
        lec.wait_();
        if (lec.hasComplexRules()) {
            List<String> categories = new ArrayList<>(tagMap.keySet());
            for (int i = 0; i < categories.size(); i++) {
                for (int j = i ; j < categories.size(); j++) {
                    String cat1 = categories.get(i);
                    String cat2 = categories.get(j);

                    ProvaList reasons1 = tagMap.get(cat1);
                    ProvaList reasons2 = tagMap.get(cat2);

                    ProvaObject[] pairwiseTermObjs = new ProvaObject[] {
                            ProvaConstantImpl.create(cat1),
                            reasons1,
                            ProvaConstantImpl.create(cat2),
                            reasons2,
                            ProvaConstantImpl.create(region)
                    };
                    ProvaList combinedTerms = ProvaListImpl.create(pairwiseTermObjs);

                    lec.executeSingleLegalQuery(messageId, combinedTerms);
                }
            }
        }

        // Final response
        String message = lec.getMessageToString();
        response.getWriter().write(message);
    }

    @Override
    public void doPut(HttpServletRequest request, HttpServletResponse response) throws IOException {

        JsonReader reader = Json.createReader(request.getInputStream());
        JsonObject root = reader.readObject();
        logger.info("Received update=" + root.toString() + " id:" + request.getRequestId());
        reader.close();
        JsonArray rulesArray = root.getJsonArray("assert");
        StringBuffer buffer = new StringBuffer();

        for (JsonValue value : rulesArray) {
            if (value.getValueType() == JsonValue.ValueType.STRING) {
                String rule = ((JsonString) value).getString();
                buffer.append(rule).append("\n");
            } else {
                response.sendError(HttpServletResponse.SC_BAD_REQUEST,"Expect JSON array of strings");
                return;
            }
        }
        String region = root.getString("location", null);
        lec.assertLaws(request.getRequestId(), region, buffer);
        response.setStatus(HttpServletResponse.SC_OK);
    }

    @Override
    public void destroy() {
    }
}
