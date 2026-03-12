import torch
from PIL import Image
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

LOCAL_MODEL_PATH = "Qwen2.5-VL-3B-Instruct" 
IMAGE_PATH = "of1.jpg"                       
# 加载本地模型，自动适配GPU/CPU，兼容3B模型
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    LOCAL_MODEL_PATH, 
    torch_dtype="auto", 
    device_map="auto",  
    trust_remote_code=True,  
    low_cpu_mem_usage=True  
)

processor = AutoProcessor.from_pretrained(
    LOCAL_MODEL_PATH,  
    trust_remote_code=True
)

local_image = Image.open(IMAGE_PATH).convert('RGB')

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": local_image, 
            },
            {"type": "text", "text": "Identify the ingredients in the image, first tell me what ingredients are in it, and then use these ingredients as the main components to create a lunch recipe suggestion for me, which should meet healthy dietary standards. You can also appropriately suggest adding or removing ingredients."},  
        ],
    }
]

text = processor.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

image_inputs, video_inputs = process_vision_info(messages)

inputs = processor(
    text=[text],
    images=image_inputs,
    videos=video_inputs,
    padding=True,
    return_tensors="pt",
)
inputs = inputs.to(model.device)  # 将输入移到模型所在设备（GPU/CPU）

generated_ids = model.generate(
    **inputs,
    max_new_tokens=512,  # 最大生成长度（按需调整）
    temperature=0.7,     # 生成随机性
    top_p=0.85,          # 核采样
    pad_token_id=processor.tokenizer.eos_token_id  
)

generated_ids_trimmed = [
    out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed,
    skip_special_tokens=True,
    clean_up_tokenization_spaces=False
)

print("===== 图片识别结果 =====")
print(output_text[0])  
