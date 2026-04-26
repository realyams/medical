---
base_model: llava-hf/llava-1.5-7b-hf
library_name: peft
model_name: medical_llava_perfect
tags:
- base_model:adapter:llava-hf/llava-1.5-7b-hf
- lora
- sft
- trl
licence: license
pipeline_tag: text-generation
---

# Model Card for medical_llava_perfect

This model is a fine-tuned version of [llava-hf/llava-1.5-7b-hf](https://huggingface.co/llava-hf/llava-1.5-7b-hf).
It has been trained using [TRL](https://github.com/huggingface/trl).

## Quick start

```python
from transformers import pipeline

question = "If you had a time machine, but could only go to the past or the future once and never return, which would you choose and why?"
generator = pipeline("text-generation", model="None", device="cuda")
output = generator([{"role": "user", "content": question}], max_new_tokens=128, return_full_text=False)[0]
print(output["generated_text"])
```

## Training procedure

[<img src="https://raw.githubusercontent.com/wandb/assets/main/wandb-github-badge-28.svg" alt="Visualize in Weights & Biases" width="150" height="24"/>](https://wandb.ai/ramykhelfaoui-university-of-boumerdas/huggingface/runs/3u0jskgt) 



This model was trained with SFT.

### Framework versions

- PEFT 0.18.1
- TRL: 1.2.0
- Transformers: 5.0.0
- Pytorch: 2.10.0+cu128
- Datasets: 4.8.3
- Tokenizers: 0.22.2

## Citations



Cite TRL as:
    
```bibtex
@software{vonwerra2020trl,
  title   = {{TRL: Transformers Reinforcement Learning}},
  author  = {von Werra, Leandro and Belkada, Younes and Tunstall, Lewis and Beeching, Edward and Thrush, Tristan and Lambert, Nathan and Huang, Shengyi and Rasul, Kashif and Gallouédec, Quentin},
  license = {Apache-2.0},
  url     = {https://github.com/huggingface/trl},
  year    = {2020}
}
```