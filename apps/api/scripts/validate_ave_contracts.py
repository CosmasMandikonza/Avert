from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass

import httpx

from app.services.ave_contracts import AVEContractError, AVEContractRiskPayload, AVEEnvelope, AVERankedTokenPayload, AVETopicPayload


DOCS_URL = "https://docs.ave.ai/reference/api-reference/v2.md"


@dataclass
class ValidationResult:
    marker: str
    endpoint: str
    count: int


def _extract_section(markdown: str, marker: str) -> str:
    start = markdown.find(marker)
    if start < 0:
        raise AVEContractError(f"Could not find docs section: {marker}")
    next_header = markdown.find("\n## ", start + len(marker))
    if next_header < 0:
        return markdown[start:]
    return markdown[start:next_header]


def _extract_first_json(section: str) -> dict:
    match = re.search(r"```json\s*(\{.*?\})\s*```", section, flags=re.DOTALL)
    if not match:
        raise AVEContractError("Could not find a JSON example block in the docs section.")
    return json.loads(match.group(1))


def validate() -> list[ValidationResult]:
    markdown = httpx.get(DOCS_URL, timeout=20.0).text
    results: list[ValidationResult] = []

    topics_payload = _extract_first_json(_extract_section(markdown, "## Get Token Rank Topics"))
    topics_envelope = AVEEnvelope.model_validate(topics_payload)
    topics = [AVETopicPayload.model_validate(item) for item in topics_envelope.data]
    results.append(
        ValidationResult(
            marker="## Get Token Rank Topics",
            endpoint="/v2/ranks/topics",
            count=len(topics),
        )
    )

    ranked_payload = _extract_first_json(_extract_section(markdown, "## Get Rank Token List By Topic"))
    ranked_envelope = AVEEnvelope.model_validate(ranked_payload)
    ranked = [AVERankedTokenPayload.model_validate(item) for item in ranked_envelope.data]
    results.append(
        ValidationResult(
            marker="## Get Rank Token List By Topic",
            endpoint="/v2/ranks?topic={topic}",
            count=len(ranked),
        )
    )

    risk_payload = _extract_first_json(_extract_section(markdown, "## Get Contract Risk Detection Report"))
    risk_envelope = AVEEnvelope.model_validate(risk_payload)
    AVEContractRiskPayload.model_validate(risk_envelope.data)
    results.append(
        ValidationResult(
            marker="## Get Contract Risk Detection Report",
            endpoint="/v2/contracts/{token-id}",
            count=1,
        )
    )

    return results


def main() -> int:
    try:
        results = validate()
    except Exception as exc:  # pragma: no cover - script-mode reporting
        print(f"AVE contract validation failed: {exc}", file=sys.stderr)
        return 1

    print("AVE contract validation passed against current official docs:")
    for result in results:
        print(f"- {result.endpoint}: validated {result.count} example payload(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
