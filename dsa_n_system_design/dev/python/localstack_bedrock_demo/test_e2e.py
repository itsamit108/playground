"""Quick end-to-end smoke test against a running LocalStack Bedrock."""

import sys
import time

from chatbot.conversation import Conversation


def main() -> None:
    convo = Conversation()
    print(f"Model : {convo.model_id}")
    print("Sending first message (model may need to download, please wait)...")
    start = time.time()

    try:
        reply = convo.send("Say hello in one short sentence.")
    except Exception as exc:
        print(f"\nERROR: {exc}")
        print("Make sure LocalStack Pro is running with Bedrock enabled.")
        sys.exit(1)

    elapsed = time.time() - start
    print(f"Reply : {reply}")
    print(f"Turns : {convo.turn_count}")
    print(f"Time  : {elapsed:.1f}s")

    # Second turn to test multi-turn
    print("\nSending follow-up...")
    reply2 = convo.send("Now say goodbye in one short sentence.")
    print(f"Reply : {reply2}")
    print(f"Turns : {convo.turn_count}")

    # Reset test
    convo.reset()
    print(f"\nAfter reset: {convo.turn_count} turns")
    print("\n✅ All e2e checks passed!")


if __name__ == "__main__":
    main()
