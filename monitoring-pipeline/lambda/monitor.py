import json
import os
import urllib.error
import urllib.request

import boto3

sns = boto3.client("sns")
TOPIC = os.environ["ALERT_TOPIC_ARN"]
TARGETS = json.loads(os.environ.get("TARGETS", "[]"))


def check(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            ok = 200 <= r.status < 400
            return ok, f"{url} -> {r.status}"
    except urllib.error.URLError as e:
        return False, f"{url} -> {e}"


def handler(event, context):
    results = [check(t) for t in TARGETS]
    failures = [msg for ok, msg in results if not ok]

    if failures:
        sns.publish(
            TopicArn=TOPIC,
            Subject="Monitor: check failures",
            Message="\n".join(failures),
        )

    return {
        "statusCode": 200,
        "body": json.dumps({"checked": len(results), "failed": len(failures)}),
    }
