from e2b_code_interpreter import Sandbox

code_to_run = """
!pip install git+https://github.com/Kroy665/es-client.git

import matplotlib.pyplot as plt
from es_client import CodeFastClient
import io

plt.plot([1, 2, 3, 4])
plt.ylabel('some numbers')
plt.savefig('test.png')
print("Done")



client = CodeFastClient(email="kroy665@gmail.com", team_slug="demo", api_key="REDACTED_ES_API_KEY")

# Get token 
client._get_token()


response = client.upload_file(file_path="test.png", file_name="test.png")
print("File uploaded successfully:")
print(response)
"""

sandbox = Sandbox()
sandbox.run_code(
  code_to_run,
  # Use `on_error` to handle runtime code errors
  on_error=lambda error: print('error:', error),
  on_stdout=lambda data: print('stdout:', data),
  on_stderr=lambda data: print('stderr:', data),
)
