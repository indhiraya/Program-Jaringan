import os
import json
import base64
from glob import glob


class FileInterface:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.files_dir = os.path.normpath(os.path.join(base_dir, 'files'))
        os.makedirs(self.files_dir, mode=0o755, exist_ok=True)
                
        if not os.path.isdir(self.files_dir):
            raise RuntimeError(f"Failed to create or access directory: {self.files_dir}")

    def list(self,params=[]):
        try:
            filelist = [os.path.basename(f) for f in glob(os.path.join(self.files_dir, '*.*'))]
            return dict(status='OK',data=filelist)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            if not filename:
                return dict(status='ERROR', data='Filename is required')
            filepath = os.path.join(self.files_dir, filename)
            with open(filepath, 'rb') as fp:
                isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            filename = params[0]
            filedata = params[1]
            decoded_data = base64.b64decode(filedata.encode())
            filepath = os.path.join(self.files_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(decoded_data)
            return dict(status='OK', data=f"{filename} uploaded successfully")
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            filepath = os.path.join(self.files_dir, filename)
            os.remove(filepath)
            return dict(status='OK', data=f"{filename} deleted successfully")
        except Exception as e:
            return dict(status='ERROR', data=str(e))

if __name__=='__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))