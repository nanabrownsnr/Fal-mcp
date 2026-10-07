"""Optional manual fal-client smoke check; pytest must never call billable APIs."""

import os

from fal_client import SyncClient


def main() -> None:
    api_key = os.environ.get("FAL_KEY")
    if not api_key:
        raise SystemExit("Set FAL_KEY before running this manual smoke check")
    result = SyncClient(api_key).subscribe(
        "fal-ai/flux/schnell",
        {"prompt": "A small red fox in a field of flowers", "image_size": "square"},
    )
    print(result)


if __name__ == "__main__":
    main()
