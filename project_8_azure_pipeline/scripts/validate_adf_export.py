from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = [
    "Account" + "Key=",
    "Shared" + "Access" + "Signature=",
    "encrypted" + "Credential",
    "subscription" + "Id",
    "tenant" + "Id",
    "client" + "Secret",
]


def load_json(relative_path: str) -> dict:
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


def assert_no_public_secrets() -> None:
    for path in (PROJECT_ROOT / "adf").rglob("*.json"):
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern in text:
                raise AssertionError(f"Sensitive pattern {pattern!r} found in {path}")


def main() -> None:
    pipeline = load_json("adf/pipeline/projectpipeline1.json")
    source_dataset = load_json("adf/dataset/DelimitedText1.json")
    sink_dataset = load_json("adf/dataset/DelimitedText2.json")
    linked_service = load_json("adf/linkedService/AzureBlobStorage1.json")

    activities = pipeline["properties"]["activities"]
    if len(activities) != 1:
        raise AssertionError("Expected exactly one ADF activity in the exported pipeline.")

    activity = activities[0]
    if activity["type"] != "Copy":
        raise AssertionError("Expected the pipeline activity to be an ADF Copy activity.")

    input_name = activity["inputs"][0]["referenceName"]
    output_name = activity["outputs"][0]["referenceName"]
    if input_name != source_dataset["name"]:
        raise AssertionError("Pipeline input dataset reference does not match source dataset.")
    if output_name != sink_dataset["name"]:
        raise AssertionError("Pipeline output dataset reference does not match sink dataset.")

    source_linked_service = source_dataset["properties"]["linkedServiceName"]["referenceName"]
    sink_linked_service = sink_dataset["properties"]["linkedServiceName"]["referenceName"]
    if source_linked_service != linked_service["name"] or sink_linked_service != linked_service["name"]:
        raise AssertionError("Datasets do not reference the exported linked service.")

    source_schema = [column["name"] for column in source_dataset["properties"]["schema"]]
    sink_schema = [column["name"] for column in sink_dataset["properties"]["schema"]]
    mappings = activity["typeProperties"]["translator"]["mappings"]
    mapped_source = [item["source"]["name"] for item in mappings]
    mapped_sink = [item["sink"]["name"] for item in mappings]
    if mapped_source != source_schema or mapped_sink != sink_schema:
        raise AssertionError("ADF column mappings do not match the source and sink schemas.")

    assert_no_public_secrets()
    print("ADF export validation passed.")


if __name__ == "__main__":
    main()
