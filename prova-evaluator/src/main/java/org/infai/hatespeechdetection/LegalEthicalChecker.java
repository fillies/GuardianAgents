package org.infai.hatespeechdetection;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import org.provarules.kernel2.ProvaList;
import org.provarules.service.EPService;
import org.provarules.service.ProvaService;
import org.provarules.service.impl.ProvaServiceImpl;

import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

public class LegalEthicalChecker implements EPService{
    private final ProvaService service;

    private final String legalRulebase = "prova/legalChecker.prova";
    private final String ethicalRulebase = "prova/ethicalChecker.prova";
    private JsonObject message = new JsonObject();
    private boolean hasComplexRules = false;

    private final Logger logger = Logger.getLogger(getClass().getName());

    public LegalEthicalChecker() {
        this.service = new ProvaServiceImpl();
        this.service.init();
        this.service.register("responding", this);
        initialize();
    }

    protected boolean hasComplexRules() {
        return hasComplexRules;
    }

    protected void resetMessage() {
        message = null;
    }

    private void initialize() {
        String legal = service.instance("legalChecker", "");
        String ethical = service.instance("ethicalChecker", "");
        service.consult(legal, legalRulebase, "legalChecker");
        service.consult(ethical, ethicalRulebase, "ethicalChecker");
        service.setGlobalConstant("legalChecker", "$Service", this);
        service.setGlobalConstant("ethicalChecker", "$Service", this);
    }

    public synchronized void resume()  {
        notifyAll();
    }

    synchronized void wait_() {
        try {
            synchronized (this) {
                wait(200);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void destroy() {
        service.destroy();
    }

    @Override
    public void send(String xid, String dest, String agent, String verb, Object payload, EPService callback) {
        logger.info(dest + " received " + verb + " from " + agent + " :" + payload);
    }

    protected void executeSingleLegalQuery(String xid, ProvaList payload) {
        service.send(xid, "legalChecker", "javaRunner", "complianceRequest", payload, this);
        wait_();
    }
    protected void executeSingleEthicalQuery(String xid, ProvaList payload) {
        service.send(xid, "ethicalChecker", "javaRunner", "complianceRequest", payload, this);
        wait_();
    }

    protected void generateHasRegionLaws(String xid, String region) {
        Map<String,String> payload = new HashMap<>();
        payload.put("hasRegion", region);
        service.send(xid, "legalChecker", "javaRunner", "informRequest", payload, this);
        wait_();
    }

    protected void assertLaws(String xid, String region, StringBuffer rules) {
        Map<String,Object> payload = new HashMap<>();
        payload.put("newRules", rules);
        payload.put("region",region);
        service.send(xid, "legalChecker", "javaRunner", "updateRequest", payload, this);
        wait_();
    }

    public void setHasRegionData(String region, String existence) {
        message = new JsonObject();
        logger.info(region + " exists: " + existence);

        if (existence.equals("true")) {
            message.addProperty("supported_location", region);
        }
        else {
            message.addProperty("unsupported_location", region);
        }
    }

    public String getMessageToString() {
        wait_();
        wait_();
        if (message == null) {
            message = new JsonObject();
        }
        if (message.isEmpty()) {
            message.addProperty("harmful", false);
        }
        return message.toString();
    }

    public void updateResponse(
            String messageId,
            String vType,
            String vCategory,
            String vSubCategory,
            String law,
            String region
    ) {
        boolean isEthical = vType.equals("ethical_violation");
        String violationTag = isEthical? "ethical_violations" : "laws_violated";
        if (message == null) {
            message = new JsonObject();
            message.addProperty("message_id", messageId);
            message.addProperty("location", region);
            // Create empty containers
            if (!isEthical) {
                message.add(vType, new JsonObject());
            }
            JsonArray lawsArr = new JsonArray();

            message.add(violationTag, lawsArr);

            logger.info(getMessageToString());
        }

        // 1. Handle vType → vCategory → [vSubCategory]
        if (!isEthical) {
            JsonObject typeObj;
            if (message.has(vType) && message.get(vType).isJsonObject()) {
                typeObj = message.getAsJsonObject(vType);
            } else {
                typeObj = new JsonObject();
                message.add(vType, typeObj);
            }

            JsonArray catArray;
            if (typeObj.has(vCategory) && typeObj.get(vCategory).isJsonArray()) {
                catArray = typeObj.getAsJsonArray(vCategory);
            } else {
                catArray = new JsonArray();
                typeObj.add(vCategory, catArray);
            }
            // Add vSubCategory if not already present
            boolean foundSub = false;
            for (JsonElement el : catArray) {
                if (el.isJsonPrimitive() && el.getAsString().equals(vSubCategory)) {
                    foundSub = true;
                    break;
                }
            }
            if (!foundSub) {
                catArray.add(vSubCategory);
            }
        }

        // 2. Handle violationTag array
        JsonArray lawsArr = message.getAsJsonArray(violationTag);
        if (lawsArr == null) {
            lawsArr = new JsonArray();
            message.add(violationTag, lawsArr);
        }
        boolean foundLaw = false;
        for (JsonElement el : lawsArr) {
            if (el.isJsonPrimitive() && el.getAsString().equals(law)) {
                foundLaw = true;
                break;
            }
        }
        if (!foundLaw) {
            lawsArr.add(law);
        }
        logger.info(message.toString());
    }

    public void triggerHasComplexRules() {
        hasComplexRules = true;
    }

    public void resetComplexRules() {
        hasComplexRules = false;
    }

    public void setMessageStatus(int status) {
        if (message == null) {
            message = new JsonObject();
        }
        message.addProperty("status", String.valueOf(status));
    }
}
