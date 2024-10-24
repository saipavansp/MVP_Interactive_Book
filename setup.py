# setup.py
import nltk
import ssl


def download_nltk_resources():
    try:
        # Disable SSL verification
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        # Download all necessary NLTK data
        print("Downloading NLTK resources...")
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('stopwords')
        print("NLTK resources downloaded successfully!")

    except Exception as e:
        print(f"Error downloading NLTK resources: {str(e)}")
        raise


if __name__ == "__main__":
    download_nltk_resources()