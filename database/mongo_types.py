import motor.motor_asyncio

# Type aliases for the Motor types, which are way too long
MongoClient = motor.motor_asyncio.AsyncIOMotorClient
MongoDatabase = motor.motor_asyncio.AsyncIOMotorDatabase
MongoCollection = motor.motor_asyncio.AsyncIOMotorCollection
