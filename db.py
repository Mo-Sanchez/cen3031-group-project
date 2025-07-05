from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


URI = (
    "mongodb+srv://app_user:RL3ddAyXHyo9WqxU@cluster0.n6mmjdr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# Create a new client and connect to the server
client = MongoClient(URI, server_api=ServerApi("1"))
db     = client["stjohn"]

# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Atlas connection OK")
except Exception as e:
    print("Atlas connection failed:", e)
