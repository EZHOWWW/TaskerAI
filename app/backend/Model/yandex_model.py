from imodel import LLModel
from transformers import AutoTokenizer, AutoModelForCausalLM


class YandexModel(LLModel):
    MODEL_NAME = "yandex/YandexGPT-5-Lite-8B-pretrain"

    def __init__(self, device: str):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME, legacy=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_NAME,
            device_map=self.device,
            torch_dtype="auto",
        )

    def generate(self, promt: str, *args, **kwargs) -> str:
        input_ids = self.tokenizer(promt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **input_ids, max_new_tokens=5120, temperature=0.3, do_sample=True
        )
        out = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return out
