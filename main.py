from server import app
import config

if __name__ == "__main__":
    print("Please wait while the server is starting...")
    app.run(host=config.API_HOST, port=config.API_PORT)
    print("Server started successfully.")
