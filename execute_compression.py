import subprocess

class ExecuteCompressionScript:
    def __init__(self, username) -> None:
        """
        Default class constructor to initialize path to node.js script.
        """
        # Your Username On The Server. You can check by the name of the directory in /home/
        self.username = username
        self.node_js_script_path = f"/home/{self.username}/pdf_compression_final.js"

    def compress_pdf(self, chat_id):
        """
        Function that executes a subprocess of the node.js script.
        """
        try:
            subprocess.run(["node", self.node_js_script_path, f"/home/{self.username}/pdfs/{chat_id}-comp.pdf", chat_id], check=True)
        except subprocess.CalledProcessError as error:
            print(f"PDF Compression Failed Due To:\n {error}")  

    # Every Part Has Default Values That Can Be Changed.
            
ExecuteCompressionScript1 = ExecuteCompressionScript()
ExecuteCompressionScript1.compress_pdf()

# Fullfill all dependencies to execute.