# Gilbreth

## Setup
### Install Darknet
1. Clone AlexeyAB's darknet repository into the deep_learning directory such that the root of the darknet repository is in the deep_learning directory. Do this by running
```
cd deep_learning
rm -rf darknet #remove any existing directories named darknet, alternatively, rename them
mkdir darknet
git clone https://github.com/AlexeyAB/darknet.git darknet
```
2. Follow the instructions in the darknet repository to build darknet for your system. In the end, you must have an executable file named darknet in the repository, such that the full path is `deep_learning/darknet/darknet`

### Set Up Cloud Vision
We use Google Cloud Vision API for our OCR operations. You therefore need to generate a token of your own for the Cloud Vision API. You can do this by following these instructions, and then storing the token in `ocr_module/gilbreth-token.json`

1. Go to the Google Cloud Console at https://console.cloud.google.com/.
2. Go to the marketplace and search for the Cloud Vision API.
3. If you're using it for the first time in the selected project, then click on enable API, otherwise click on Manage.
4. The next screen will show all API keys, OAuth client IDs and Service account associated with the API and the project. Press on create credentials.
5. This will let you create a new Service Account. After creating it, select the Key Type as JSON. Click the `create` button, and the JSON token will start downloading.

Once the token is downloaded and stored as `ocr_module/gilbreth-token.json`, install the python packages for Google Cloud Vision.
```
pip install google-cloud-vision protobuf google-api-core google-auth
```

### Set Up Open-CV (optional)
For running the 4-point perspective transform (only in the case of skewed flowcharts), you will need to install OpenCV for your device.

## Running the Program

In case of a skewed flowchart, straighten it using the 4-point perspective transform provided in deep_learning/preprocessing

Then run
```
python gilbreth.py <image path>
```

For example-
```
python gilbreth.py fc_dirs/flowcharts/Flowcharts\ 1\ to\ 4\ \(1\).jpg
```