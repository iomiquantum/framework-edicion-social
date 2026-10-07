---
license: gemma
library_name: transformers
pipeline_tag: image-text-to-text
extra_gated_heading: Access Gemma on Hugging Face
extra_gated_prompt: To access Gemma on Hugging Face, you’re required to review and
  agree to Google’s usage license. To do this, please ensure you’re logged in to Hugging
  Face and click below. Requests are processed immediately.
extra_gated_button_content: Acknowledge license
base_model: google/gemma-3n-E4B-it
tags:
- automatic-speech-recognition
- automatic-speech-translation
- audio-text-to-text
- video-text-to-text
- mlx
---

# mlx-community/gemma-3n-E2B-it-4bit
This model was converted to MLX format from [`google/gemma-3n-E2B-it`]() using mlx-vlm version **0.3.1**.
Refer to the [original model card](https://huggingface.co/google/gemma-3n-E2B-it) for more details on the model.
## Use with mlx

```bash
pip install -U mlx-vlm
```

```bash
python -m mlx_vlm.generate --model mlx-community/gemma-3n-E2B-it-4bit --max-tokens 100 --temperature 0.0 --prompt "Describe this image." --image <path_to_image>
```
