from transformers import pipeline


def main():
    # Load a pre-trained sentiment analysis model
    classifier = pipeline("sentiment-analysis", device=0)

    # Classify the sentiment of a piece of text
    result = classifier("I really enjoyed this movie!")
    print(result)


if __name__ == "__main__":
    main()
