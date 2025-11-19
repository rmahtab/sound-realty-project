import argparse
import requests
import pandas as pd


# Endpoint URL (Docker/local)
URL = "http://127.0.0.1:8000/predict"


def test_predict(url, n=5, random_state=None):
    # Load test examples
    df = pd.read_csv("future_unseen_examples.csv")
    test_df = df.sample(n=n, replace=False, random_state=random_state)

    print(f"Loaded {len(test_df)} randomly sampled records out of {len(df)} total unseen test records to test /predict endpoint\n")

    # Iterate through rows
    for i, row in test_df.iterrows():
        payload = row.to_dict()

        print(f"Sending row {i}: {payload}")

        try:
            response = requests.post(url, json=payload)
            print("Response:", response.json())
        except Exception as e:
            print("Error:", e)

        print("-" * 40)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--random_state", type=int, default=None)
    args = parser.parse_args()

    test_predict(URL, n=args.n, random_state=args.random_state)
