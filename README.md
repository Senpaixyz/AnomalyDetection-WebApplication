# Network Traffic Anomaly Detection

The study delves into analyzing network traffic behavior, identifying potential attacks, understanding their mechanisms, and evaluating their impact on target machines. Sample datasets were collected and analyzed using Wireshark tools to facilitate clustering. Following this, datasets were filtered using Jupyter Notebook and Anaconda Navigator to train algorithms like KNN and SVM for anomaly detection. The development phase involved creating a model with KNN and integrating it into a cloud-based web application, leveraging Firebase's SMS API and Semaphore for functionality. Subsequently, various Linux attacks such as UDP, Synflood, FindFlood, Reset Flood, LOIC, Push Ach, and Sinfin Flood were tested, showcasing commendable results in terms of the model's effectiveness in detecting and mitigating these assaults.

![Anomaly Detection Severe](https://github.com/Senpaixyz/AnomalyDetection-WebApplication/blob/master/static/screenshots/AttackSimulation_Moment-severe.jpg?raw=true)


## Installation

Install the dependencies and devDependencies before starting the server. To avoid module issues, ensure that the Python version installed on your machine is Python 3.6.8.
> Note: Check to see whether you've already built a virtual environment, or download Pycharms IDE and launch this project.

```sh
git clone https://github.com/Senpaixyz/AnomalyDetection-WebApplication.git
```
```sh
cd AnomalyDetection-WebApplication
```
```sh
pip install requirements.txt
```

### Server.
This code allows you to start monitor mode on your Windows OS . If your machine is not running in Windows, you can skip this step. If you encounter any errors when running the code below, please install [npcap](https://npcap.com/) and download Microsoft Visual C++ 14.0 or above. Run the code below until the console displays "NPCAP Service Started."


```sh
net start npcap
```
Open your favorite Terminal and run these commands.

```sh
python app.py
```

Open the server and go to that local server URL.

```sh
http://127.0.0.1:5000/
```

#### API Configuration
Make sure you followed the PDF method for firebase configuration. However, you must wait 2-4 working days for Semaphore to offer you 10 SMS credits for trial. For testing purposes, I kept all of my API keys inside the Python file, but you are free to create .ENV files to secure your keys.

| Firebase  | [Using Firebase for Anomaly Detection.pdf](https://github.com/Senpaixyz/AnomalyDetection-WebApplication/tree/master/static/pdf) |
| SMS API  | [Semaphore](https://semaphore.co/#user) |



