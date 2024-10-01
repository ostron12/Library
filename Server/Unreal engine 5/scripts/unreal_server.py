import unreal
import socket
import base64
import os
import threading

class UnrealServer:
    def __init__(self):
        self.server_socket = None
        self.server_thread = None
        self.running = False

    def handle_client_connection(self, conn):
        try:
            data = b""
            while True:
                part = conn.recv(4096)
                if not part:
                    break
                data += part
            conn.close()

            message = data.decode('utf-8').split('\n')
            folder_name, file_name, *texture_data, file_content_base64 = message

            # Decode the file content
            file_content = base64.b64decode(file_content_base64 + '=' * (-len(file_content_base64) % 4))

            # Define the save path
            save_path = os.path.join(unreal.Paths.project_content_dir(), "Imported", file_name)
            unreal.log(f"Save path: {save_path}")

            # Ensure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save the received file
            with open(save_path, 'wb') as f:
                f.write(file_content)
            unreal.log(f"File saved: {save_path}")

            # Process and save textures
            for texture in texture_data:
                texture_name, texture_base64 = texture.split(':')
                texture_content = base64.b64decode(texture_base64 + '=' * (-len(texture_base64) % 4))
                texture_save_path = os.path.join(unreal.Paths.project_content_dir(), "Imported", texture_name)
                with open(texture_save_path, 'wb') as f:
                    f.write(texture_content)
                unreal.log(f"Texture saved: {texture_save_path}")

            # Use execute_console_command to import the FBX file on the game thread
            command = 'py "import import_automation; import_automation.ImportAutomationLibrary.import_fbx_automated(\'{}\')"'.format(save_path.replace("\\", "/"))
            unreal.SystemLibrary.execute_console_command(None, command)

        except Exception as e:
            unreal.log(f"Failed to process the received data: {e}")

    def start_server(self):
        if self.running:
            unreal.log("Server is already running.")
            return

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind(('localhost', 6001))  # Use port 6001
            self.server_socket.listen(5)  # Allow up to 5 connections in the queue
            self.running = True
            unreal.log("Server is listening on port 6001...")

            while self.running:
                conn, addr = self.server_socket.accept()
                unreal.log(f"Connection from {addr}")
                client_thread = threading.Thread(target=self.handle_client_connection, args=(conn,))
                client_thread.start()
        except Exception as e:
            unreal.log(f"Failed to start server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def run_server(self):
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop_server(self):
        if not self.running:
            unreal.log("Server is not running.")
            return

        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.server_thread:
            self.server_thread.join()
        unreal.log("Server stopped")

# Create an instance of the UnrealServer
server_instance = UnrealServer()

def start_server():
    server_instance.run_server()

def stop_server():
    server_instance.stop_server()

if __name__ == "__main__":
    start_server()
