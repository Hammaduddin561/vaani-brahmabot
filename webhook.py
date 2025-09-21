# webhook.py

import os
import logging

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from neo4j import GraphDatabase

from cypher_engine import generate_cypher

# configure logger
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter()

# initialize Neo4j driver
driver = GraphDatabase.driver(
    os.getenv("NEO_URI"),
    auth=(os.getenv("NEO_USER"), os.getenv("NEO_PASS"))
)

# Twilio request validator
validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))


@router.post("/whatsapp")
async def whatsapp_reply(request: Request):
    # parse Twilio’s incoming form
    form = await request.form()
    params = dict(form)
    url = str(request.url)
    signature = request.headers.get("X-Twilio-Signature", "")

    # verify Twilio signature
    if not validator.validate(url, params, signature):
        logger.warning("Invalid Twilio signature for %s", url)
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    from_number = form.get("From", "")
    incoming_msg = form.get("Body", "").strip()
    logger.info("📥 From %s: %s", from_number, incoming_msg)

    # generate the appropriate Cypher query
    cypher = generate_cypher(incoming_msg)
    logger.debug("🔍 Generated Cypher:\n%s", cypher)

    resp = MessagingResponse()
    msg = resp.message()

    # built-in greeting
    if cypher == "__greeting__":
        msg.body("👋 Hey there! I’m Vaani, your space-savvy assistant.")
        return Response(str(resp), media_type="application/xml")

    # built-in vague prompt
    if cypher == "__vague__":
        msg.body("🌌 Curious? Try: “List satellites launched by ISRO.”")
        return Response(str(resp), media_type="application/xml")

    # empty or unrecognized
    if not cypher.strip():
        msg.body("🤖 I didn’t quite catch that. Send ‘Hi’ for examples.")
        return Response(str(resp), media_type="application/xml")

    try:
        # execute the Cypher query
        with driver.session() as session:
            result = session.run(cypher)
            records = [record.data() for record in result]

        logger.info("🎯 Records returned: %s", records)

        # no matches
        if not records:
            msg.body("✅ I looked, but found no matching data.")
            return Response(str(resp), media_type="application/xml")

        # format your results
        lines = []
        for rec in records:
            # extract known fields
            name      = rec.get("m.name")      or rec.get("name")
            objective = rec.get("m.objective") or rec.get("objective")
            status    = rec.get("m.status")    or rec.get("status")
            year      = rec.get("m.launch_year") or rec.get("launch_year")

            # detail-style: name + objective/status
            if name and (objective or status):
                parts = [name]
                if objective:
                    parts.append(objective)
                if status:
                    parts.append(f"({status})")
                lines.append("• " + " – ".join(parts))
            # date-filtered style: name + year
            elif name and year:
                lines.append(f"• {name} (launched in {year})")
            # fallback: list any string/int fields
            else:
                for v in rec.values():
                    if isinstance(v, (str, int)):
                        lines.append(f"• {v}")

        msg.body("✅ Here’s what I found:\n" + "\n".join(lines))
        return Response(str(resp), media_type="application/xml")

    except Exception as e:
        logger.error("Execution error: %s", e)
        msg.body(f"❌ Oops! Something broke:\n{e}")
        return Response(str(resp), media_type="application/xml")