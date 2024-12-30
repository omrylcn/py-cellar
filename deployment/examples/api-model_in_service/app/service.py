import onnxruntime as ort
from app.config import MODEL_PATH
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
import numpy as np
import warnings


warnings.filterwarnings("ignore", category=UserWarning, module="onnxruntime")
ort.set_default_logger_severity(3)  # 3 = ERROR, will suppress warnings


class ImageService:
    def __init__(self, model_path: str=MODEL_PATH):
        self.session = ort.InferenceSession(model_path)


    async def infer(self,file: UploadFile,image_size:tuple=(224,224)):



         # Read image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        image = image.resize((image_size,image_size),resample=Image.Resampling.LANCZOS)


        x = np.array(image).astype('float32')
        x = np.transpose(x, [2, 0, 1])
        x = np.expand_dims(x, axis=0)
        
        # Get input and output names
        output_name = self.session.get_outputs()[0].name
        input_name = self.session.get_inputs()[0].name


        result = self.session.run([output_name], {input_name: x})[0][0]

        # Postprocess
        result = np.clip(result, 0, 255)
        result = result.transpose(1, 2, 0).astype("uint8")
        
        return Image.fromarray(result)